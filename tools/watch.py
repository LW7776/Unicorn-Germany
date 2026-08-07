"""Scans allowlisted trade-press feeds for anything that might change the dataset.

It never edits a company file. It produces a candidate list for a human to act on,
which is what keeps an automated pipeline safe.

Run: python3 tools/watch.py
"""
import datetime as dt
import email.utils
import json
import pathlib
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

# Allow `python3 tools/watch.py` to resolve `tools.schema`-style imports even though
# running a script puts only its own directory on sys.path, not the repo root. pytest
# is unaffected (pytest.ini already puts the repo root on sys.path via pythonpath = .).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

FEEDS = {
    "Sifted": "https://sifted.eu/feed",
    "EU-Startups": "https://www.eu-startups.com/feed/",
    "Tech.eu": "https://tech.eu/feed/",
    "TechCrunch": "https://techcrunch.com/feed/",
    "Gründerszene": "https://www.businessinsider.de/gruenderszene/feed/",
}

# English + German trigger words. German is on the allowlist specifically for
# Gründerszene, so it needs its own vocabulary, not a coincidental match on an
# English loanword like "Unicorn". "sammelt ... ein" is the separable-prefix verb
# "einsammeln" (to raise); the two halves can be many words apart in a headline
# ("sammelt 50 Millionen Euro in Serie-C-Runde ein"), so it is matched as
# "sammelt", then up to ~80 characters, then "ein" — not bare "ein" alone, which
# is far too common a word (indefinite article) to use as a standalone signal.
FUNDING_SIGNAL = re.compile(
    r"\b(raise[sd]?|raising|funding|series[\s-]?[a-g]|serie[\s-]?[a-g]|valuation|bewertung|"
    r"unicorn|ipo|börsengang\w*|acquire[sd]?|acquisition|übernahme\w*|übernimmt\w*|"
    r"insolven\w+|finanzierungsrunde\w*)\b"
    r"|\bsammelt\b.{0,80}?\bein\b",
    re.I)

# Any number at billion scale, not just one that literally starts with the digit
# "1" — "$10bn", "€25bn" and "$1.35bn" must all match; a seed-round "$5m" must not,
# so this is deliberately not widened to millions. Currency is required alongside
# an English "bn"/"billion" figure (keeps a bare "10bn" reference to something
# unrelated from firing); German "Milliarde(n)" is unambiguous enough on its own
# that no currency marker is required. "Milliarden-Bewertung" (and the unhyphenated
# compound "Milliardenbewertung") is matched even with no explicit number, the same
# way bare "unicorn"/"Einhorn" is — both are shorthand German trade-press phrasing
# for "reached a billion-euro valuation".
NEW_UNICORN_SIGNAL = re.compile(
    r"(?:\$|€|eur|usd)\s?\d+(?:[.,]\d+)?\s?(?:bn|billion)"
    r"|\d+(?:[.,]\d+)?\s?milliarden?\b"
    r"|milliarden?-?bewertung"
    r"|\bunicorn\b|\beinhorn\b",
    re.I)

USER_AGENT = "german-unicorns-watch/1.0 (+https://github.com)"
MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # a well-formed RSS/Atom feed is well under this; caps a misbehaving origin
ATOM_NS = "{http://www.w3.org/2005/Atom}"


def _parse_date(raw):
    raw = (raw or "").strip()
    if not raw:
        return ""
    try:                                            # RSS: RFC 822, e.g. "Wed, 13 Mar 2024 09:00:00 GMT"
        return email.utils.parsedate_to_datetime(raw).date().isoformat()
    except (TypeError, ValueError):
        pass
    try:                                            # Atom: ISO 8601, e.g. "2024-03-13T09:00:00Z"
        iso = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
        return dt.datetime.fromisoformat(iso).date().isoformat()
    except ValueError:
        return ""


def _atom_link(node):
    for tag in (f"{ATOM_NS}link", "link"):
        for link_el in node.findall(tag):
            href = link_el.get("href")
            rel = link_el.get("rel")
            if href and rel in (None, "alternate"):
                return href
    return ""


def parse_feed(xml_text, source):
    """Parses RSS <item> elements or, failing that, Atom <entry> elements.

    A dead source that returns something other than RSS or Atom (a WAF page, a
    schema change, an empty document) legitimately parses to zero items here —
    scan() is responsible for turning that into a feedErrors entry rather than
    letting it look like a quiet month.
    """
    root = ET.fromstring(xml_text)
    items = []

    rss_items = list(root.iter("item"))
    if rss_items:
        for node in rss_items:
            items.append({
                "title": (node.findtext("title") or "").strip(),
                "link": (node.findtext("link") or "").strip(),
                "published": _parse_date(node.findtext("pubDate")),
                "source": source,
            })
        return items

    atom_entries = list(root.iter(f"{ATOM_NS}entry")) or list(root.iter("entry"))
    for node in atom_entries:
        title = (node.findtext(f"{ATOM_NS}title") or node.findtext("title") or "").strip()
        published = (node.findtext(f"{ATOM_NS}published") or node.findtext("published") or
                     node.findtext(f"{ATOM_NS}updated") or node.findtext("updated") or "")
        items.append({
            "title": title,
            "link": _atom_link(node),
            "published": _parse_date(published),
            "source": source,
        })
    return items


def _name_pattern(name):
    # A word-boundary match, not a bare substring check: a tracked company called
    # "Flix" would otherwise be flagged by every "FlixBus" headline, and noise is
    # what makes a human stop reading the monthly issue. \b works for the names in
    # this dataset (letters/digits/GmbH-style tokens); it is not a full Unicode
    # word-segmentation, which this project does not need. Note a name that starts
    # or ends in punctuation (e.g. leading/trailing quote marks) would never match
    # under \b, since \b requires a word-character boundary at that edge — not a
    # concern for the slugs currently tracked, but worth knowing if one is added.
    return re.compile(r"\b" + re.escape(name) + r"\b", re.I)


def match_candidates(items, companies):
    names = {c["name"]: c["slug"] for c in companies}
    patterns = {name: _name_pattern(name) for name in names}
    candidates = []
    for item in items:
        title = item["title"]
        funding_match = FUNDING_SIGNAL.search(title)
        if not funding_match and not NEW_UNICORN_SIGNAL.search(title):
            continue
        slug = next((names[name] for name in names if patterns[name].search(title)), None)
        if slug:
            candidates.append({**item, "company": slug,
                               "reason": f"tracked company mentioned: {funding_match.group(0) if funding_match else 'signal'}"})
        elif NEW_UNICORN_SIGNAL.search(title):
            candidates.append({**item, "company": None,
                               "reason": "possible new unicorn — not currently tracked"})
    return candidates


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read(MAX_RESPONSE_BYTES).decode("utf-8", "replace")


def scan(feeds=None, companies=None, out="data/candidates.json"):
    feeds = feeds or FEEDS
    if companies is None:
        companies = [json.loads(f.read_text(encoding="utf-8"))
                     for f in sorted(pathlib.Path("data/companies").glob("*.json"))]
    items, errors = [], []
    for source, url in feeds.items():
        try:
            feed_items = parse_feed(fetch(url), source)
        except Exception as exc:                      # a dead feed must not fail the run
            errors.append(f"{source}: {exc}")
            continue
        if not feed_items:                            # well-formed but empty must not look like a quiet month
            errors.append(f"{source}: parsed but contained no items (schema change or error page?)")
            continue
        items.extend(feed_items)
    payload = {
        "scannedOn": dt.date.today().isoformat(),
        "feedErrors": errors,
        "candidates": match_candidates(items, companies),
    }
    pathlib.Path(out).write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = scan()
    print(f"{len(result['candidates'])} candidate(s); {len(result['feedErrors'])} feed error(s)")
    for error in result["feedErrors"]:
        print(f"! {error}")
    for candidate in result["candidates"]:
        print(f"- [{candidate['source']}] {candidate['title']} -> {candidate['company'] or 'NEW'}")
