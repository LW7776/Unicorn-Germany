"""The punctuation ban, enforced rather than remembered.

docs/BRAND.md: no em dash and no semicolon in anything a reader sees. Both are
easy to type and impossible to spot in a diff, and the site's copy is written in
JSON files by hand and by an automated drafter, so the rule needs a test rather
than a habit.

Two things are deliberately outside the ban, and both are checked here rather
than merely skipped:

  Source titles are quotations. A publication that put an em dash in its own
  headline wrote that headline, and editing it to suit our house style would
  falsify a citation on a site whose whole claim is that its citations are exact.
  Titles are checked against a named allowlist instead, so an existing one stays
  and a new one has to be looked at by a person.

  Source quotes are not rendered anywhere (detail.js prints title, publication
  and date), so they are out of scope entirely and stay verbatim.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
BANNED = {"em dash": "—", "semicolon": ";"}

# Titles that carry banned punctuation because their publisher wrote them that
# way. Each is a verbatim headline.
TITLES_QUOTED_VERBATIM = {
    "Laying the Foundations for Visual Intelligence—Our $300M Series B",
}

HTML_PAGES = ["index.html", "about.html", "impressum.html"]
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
# `&nbsp;` is markup, not a semicolon anybody reads.
HTML_ENTITY = re.compile(r"&(?:#\d+|#x[0-9a-fA-F]+|[a-zA-Z][a-zA-Z0-9]*);")


def _company_copy():
    """(where, text) for every company field a reader actually sees."""
    for file in sorted((ROOT / "data" / "companies").glob("*.json")):
        record = json.loads(file.read_text(encoding="utf-8"))
        slug = file.stem
        yield f"{slug}.name", record["name"]
        yield f"{slug}.niche", record["niche"]
        yield f"{slug}.hq.city", record["hq"]["city"]
        for sector in record["sectors"]:
            yield f"{slug}.sectors", sector
        for city in record.get("alsoBasedIn") or []:
            yield f"{slug}.alsoBasedIn", city
        for key in ("problem", "solution"):
            yield f"{slug}.thesis.{key}", record["thesis"][key]
        for founder in record["founders"]:
            yield f"{slug}.founders.role", founder["role"]
        for investor in record["investors"]:
            yield f"{slug}.investors", investor
        containers = [("valuation", record["valuation"])]
        containers += [(f"round {r['id']}", r) for r in record["rounds"]]
        for label, container in containers:
            for key in ("disputed", "undisclosed"):
                if container.get(key):
                    yield f"{slug}.{label}.{key}.note", container[key]["note"]
            if container.get("stage"):
                yield f"{slug}.{label}.stage", container["stage"]


def _funding_copy():
    for file in sorted((ROOT / "data" / "funding").glob("*.json")):
        record = json.loads(file.read_text(encoding="utf-8"))
        for group in ("lead", "more"):
            for entry in record[group]:
                where = f"{file.stem}.{group}.{entry['id']}"
                yield f"{where}.company", entry["company"]
                if entry.get("text"):
                    yield f"{where}.text", entry["text"]
                if entry.get("stage"):
                    yield f"{where}.stage", entry["stage"]
                if entry.get("note"):
                    yield f"{where}.note.text", entry["note"]["text"]


def _offences(pairs):
    return [
        f"{where}: {name}"
        for where, text in pairs
        for name, char in BANNED.items()
        if char in (text or "")
    ]


def test_no_banned_punctuation_in_company_copy():
    assert _offences(_company_copy()) == []


def test_no_banned_punctuation_in_the_funding_writeups():
    assert _offences(_funding_copy()) == []


def test_no_banned_punctuation_in_the_static_pages():
    """HTML comments are notes to the next maintainer, not copy, and character
    references are markup, so both come out before the check."""
    pairs = []
    for page in HTML_PAGES:
        source = (ROOT / page).read_text(encoding="utf-8")
        pairs.append((page, HTML_ENTITY.sub("", HTML_COMMENT.sub("", source))))
    assert _offences(pairs) == []


def test_a_source_title_keeps_its_publishers_punctuation():
    """Not an exemption anyone can widen by accident: a new headline carrying a
    banned character fails here until somebody decides it really is verbatim."""
    found = set()
    for file in sorted((ROOT / "data" / "companies").glob("*.json")):
        for source in json.loads(file.read_text(encoding="utf-8"))["sources"]:
            if any(char in source["title"] for char in BANNED.values()):
                found.add(source["title"])
    for file in sorted((ROOT / "data" / "funding").glob("*.json")):
        record = json.loads(file.read_text(encoding="utf-8"))
        for group in ("lead", "more"):
            for entry in record[group]:
                for source in [entry["source"]] + (
                        [entry["note"]["source"]] if entry.get("note") else []):
                    if any(char in source["title"] for char in BANNED.values()):
                        found.add(source["title"])
    assert found == TITLES_QUOTED_VERBATIM
