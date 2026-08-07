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
FUNDING_SIGNAL = re.compile(
    r"\b(raise[sd]?|raising|funding|series\s+[a-g]|valuation|unicorn|"
    r"ipo|acquire[sd]?|acquisition|insolven\w+)\b", re.I)
NEW_UNICORN_SIGNAL = re.compile(r"(\$|€|eur|usd)\s?1(\.\d)?\s?(bn|billion)|unicorn", re.I)
USER_AGENT = "german-unicorns-watch/1.0 (+https://github.com)"


def parse_feed(xml_text, source):
    root = ET.fromstring(xml_text)
    items = []
    for node in root.iter("item"):
        published = (node.findtext("pubDate") or "").strip()
        try:
            date = email.utils.parsedate_to_datetime(published).date().isoformat()
        except (TypeError, ValueError):
            date = ""
        items.append({
            "title": (node.findtext("title") or "").strip(),
            "link": (node.findtext("link") or "").strip(),
            "published": date,
            "source": source,
        })
    return items


def _name_pattern(name):
    # A word-boundary match, not a bare substring check: a tracked company called
    # "Flix" would otherwise be flagged by every "FlixBus" headline, and noise is
    # what makes a human stop reading the monthly issue. \b works for the names in
    # this dataset (letters/digits/GmbH-style tokens); it is not a full Unicode
    # word-segmentation, which this project does not need.
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
        return response.read().decode("utf-8", "replace")


def scan(feeds=None, companies=None, out="data/candidates.json"):
    feeds = feeds or FEEDS
    if companies is None:
        companies = [json.loads(f.read_text(encoding="utf-8"))
                     for f in pathlib.Path("data/companies").glob("*.json")]
    items, errors = [], []
    for source, url in feeds.items():
        try:
            items.extend(parse_feed(fetch(url), source))
        except Exception as exc:                      # a dead feed must not fail the run
            errors.append(f"{source}: {exc}")
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
