"""Gathers one week of German funding candidates from the allowlisted feeds.

Run: python3 tools/weekly_funding.py --last-complete-week
     python3 tools/weekly_funding.py --week 2026-W30 --report candidates.json
     python3 tools/weekly_funding.py --last-complete-week --today 2026-08-10

THIS FILE NO LONGER WRITES THE SITE
-----------------------------------
It used to draft a week of the round-up: fetch the feeds, ask Claude to pick and
write the lead rounds, verify every claim back against the fetched text, write
`data/funding/<week>.json` and open a pull request. That whole path is gone,
along with the workflow that ran it.

The reason is quality, not cost. Writing a week is a model call, and the
operator holds no API key, so the scheduled job could only ever publish a bare
list of parsed headlines — visibly thinner than the weeks a person wrote. A
register that degrades a little every Monday is worse than one updated by hand,
so CI stopped producing content: it now scans the feeds, and if there is
anything to report it opens one issue saying so. A person and an assistant
write the week and push it.

What is left here is the gathering half, which is exactly what that person
needs, and what .github/workflows/monday-reminder.yml runs to fill the issue:

  last_complete_week  which ISO week a Monday is reporting on
  collect             every allowlisted-feed article published inside a week
                      that mentions Germany and a funding event, body text and
                      all, so a human reader (or their assistant) can work from
                      the reporting rather than from a headline
  read_headline       a mechanical reading of one headline into a round, used to
                      say "this looks like a closed round for X, EUR 12m" beside
                      a link. It fails closed: an ambiguous headline yields
                      None and the article is still listed, just unparsed.
  candidates          the two together, plus the register cross-check, as the
                      JSON the Monday issue is built from

Nothing here decides anything. It produces a list for a person to act on, which
is the same division of labour tools/watch.py has always had.
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools.schema import SOURCE_ALLOWLIST
from tools.validate_funding import week_bounds
from tools.watch import FEEDS, _name_pattern, fetch, parse_feed

# How many articles to keep. The feeds return far more than a week's German
# funding news, and the filter below is deliberately permissive — better to hand
# over a few irrelevant articles than to filter out the one round that mattered
# with a regex. A person skims the list; a regex cannot un-drop an article.
MAX_ARTICLES = 80

# How many pages of each feed to walk. A feed's front page holds about ten
# items, which on a busy publication is a day and a half — so a Monday run
# looking back over the whole of last week would simply not see Tuesday.
# `?paged=N` is the WordPress convention several of these publications use;
# a feed that does not understand it just returns page one again, and the
# link-level dedupe below absorbs that. No per-publication special-casing.
FEED_PAGES = 5

# Germany, in the vocabulary the trade press actually uses. This is a *recall*
# filter, not a nationality test: what it must not do is drop a real German
# round. Deciding whether a company is German enough to publish is the job of
# the person reading the issue — the same division of labour tools/watch.py
# already documents for its own scan.
GERMAN_HINT = re.compile(
    r"\bGerman(?:y|-based)?\b|\bDeutsch\w*\b|\bBerlin\b|\bMunich\b|\bMünchen\b|"
    r"\bHamburg\b|\bCologne\b|\bKöln\b|\bFrankfurt\b|\bStuttgart\b|\bLeipzig\b|"
    r"\bDüsseldorf\b|\bKarlsruhe\b|\bDresden\b|\bHeidelberg\b|\bAachen\b|"
    r"\bBremen\b|\bHannover\b|\bNuremberg\b|\bNürnberg\b|\bPotsdam\b|\bDACH\b",
    re.I)

FUNDING_HINT = re.compile(
    r"\braise[sd]?\b|\braising\b|\bfunding\b|\bseed\b|\bseries\s+[a-g]\b|"
    r"\bpre-seed\b|\bsecure[sd]?\b|\bland[s]?\b|\bclose[sd]?\s+a\b|\bround\b|"
    r"\bmillion\b|\bbillion\b|\bMillionen\b|\bFinanzierungsrunde\b",
    re.I)


# --- collecting -------------------------------------------------------------

def last_complete_week(today):
    """The ISO week that ended before `today`. Monday's run covers the week just
    finished, not the one it is standing in. `today` is passed in rather than
    read from the clock so this is testable and so a past week can be replayed."""
    monday = today - dt.timedelta(days=today.weekday())
    ended = monday - dt.timedelta(days=1)          # the Sunday just gone
    year, week, _ = ended.isocalendar()
    return f"{year}-W{week:02d}"


def collect(week, feeds=None, fetcher=None):
    """Every article the allowlisted feeds published inside `week`.

    Returns (articles, errors). A dead feed is an error, never an exception: one
    publication having a bad morning must not cost the whole week.
    """
    start, end = week_bounds(week)
    feeds = feeds or FEEDS
    fetcher = fetcher or fetch
    articles, errors = [], []
    for source, url in feeds.items():
        if source not in SOURCE_ALLOWLIST:
            errors.append(f"{source}: not on the source allowlist; skipped")
            continue
        items, seen_links, failures = [], set(), []
        for page in range(1, FEED_PAGES + 1):
            paged = url if page == 1 else (
                f"{url}{'&' if '?' in url else '?'}paged={page}")
            try:
                batch = parse_feed(fetcher(paged), source)
            except Exception as exc:                # noqa: BLE001 - see docstring
                failures.append(str(exc))
                break                               # a broken page ends the walk
            fresh = [item for item in batch if item["link"] not in seen_links]
            if not fresh:
                break                               # paging unsupported, or exhausted
            seen_links.update(item["link"] for item in fresh)
            items.extend(fresh)

        if failures and not items:
            errors.append(f"{source}: {failures[0]}")
            continue
        if not items:
            errors.append(f"{source}: parsed but contained no items "
                          f"(schema change or error page?)")
            continue
        for item in items:
            if not (start <= item["published"] <= end):
                continue
            blob = f"{item['title']} {item.get('summary', '')}"
            if not (GERMAN_HINT.search(blob) and FUNDING_HINT.search(blob)):
                continue
            articles.append({
                "id": f"a{len(articles) + 1}",
                "publication": source,
                "title": item["title"],
                "url": item["link"],
                "publishedOn": item["published"],
                "text": item.get("summary", ""),
            })
    # Longest first: an article with the full body is far more useful to a
    # reader than a headline-only stub, and the cap has to fall on the stubs
    # rather than on whichever feed happened to be polled last.
    articles.sort(key=lambda a: len(a["text"]), reverse=True)
    return articles[:MAX_ARTICLES], errors


# --- reading a headline, with no model in the loop --------------------------
#
# Everything below is deliberately mechanical. It reads a company name, an
# amount and a currency out of an article's own headline so the Monday issue can
# say what a link is probably about. It emits nothing it could not point at in
# that headline, and every step fails closed: an ambiguous headline yields None.
# Nothing here is published — an unparsed article is still listed in the issue
# under its own headline, so a miss costs a line of annotation, not a round.

# Amounts. Both orders occur in the trade press: "€12 million" (English) and
# "50 Millionen Euro" (German). A scale word is *required* in both — a bare
# "€12" is not a round size anyone can rely on, and reading it as millions
# would be an assumption rather than a reading.
_SCALES = {
    "m": 1, "mn": 1, "million": 1, "millions": 1, "millionen": 1,
    "b": 1000, "bn": 1000, "billion": 1000, "billions": 1000,
    "milliarde": 1000, "milliarden": 1000,
}
_SCALE_WORDS = "|".join(sorted(_SCALES, key=len, reverse=True))
_NUMBER = r"\d{1,4}(?:[.,]\d{1,3})?"

AMOUNT_CURRENCY_FIRST = re.compile(
    rf"(?P<currency>€|\$|\bEUR\b|\bUSD\b)\s?(?P<number>{_NUMBER})\s?"
    rf"(?P<scale>{_SCALE_WORDS})\b", re.I)
AMOUNT_CURRENCY_LAST = re.compile(
    rf"(?P<number>{_NUMBER})\s?(?P<scale>{_SCALE_WORDS})\b[\s-]?"
    rf"(?P<currency>€|\$|\bEUR\b|\bUSD\b|euros?|dollars?)", re.I)

_CURRENCIES = {"€": "EUR", "$": "USD", "eur": "EUR", "usd": "USD",
               "euro": "EUR", "euros": "EUR", "dollar": "USD", "dollars": "USD"}

# "over €10 million", "rund 50 Millionen": the figure is a boundary, not the
# round. The register's `approximate` flag exists exactly for this, and the
# renderer prints "about" beside such a number rather than stating it flat.
APPROXIMATE_HINT = re.compile(
    r"\bover\b|\bmore than\b|\bnearly\b|\balmost\b|\baround\b|\babout\b|"
    r"\bup to\b|\bat least\b|\bunder\b|\brund\b|\bknapp\b|\bmehr als\b|"
    r"\büber\b|\bfast\b|~", re.I)

# The verb that separates the company from the round. Everything before the
# first match is the candidate name; everything after is the round.
RAISE_VERB = re.compile(
    r"\b(?:raises|raised|secures|secured|lands|landed|closes|closed|bags|"
    r"bagged|nets|netted|scores|scored|snags|snagged|picks up|picked up|"
    r"pockets|pocketed|banks|banked|sammelt|erhält|bekommt|sichert|holt)\b",
    re.I)

# Headline furniture that sits between a publication's own framing and the
# company: "Exclusive: ", "Berlin-based ", "German AI startup ". Stripped
# iteratively from the front of the candidate.
LEADING_LABEL = re.compile(r"^\s*(?:exclusive|breaking|scoop|update|just in)\s*[:\-–—]\s*", re.I)
GERMAN_CITIES = {
    "berlin", "munich", "münchen", "hamburg", "cologne", "köln", "frankfurt",
    "stuttgart", "leipzig", "düsseldorf", "dusseldorf", "karlsruhe", "dresden",
    "heidelberg", "aachen", "bremen", "hannover", "hanover", "nuremberg",
    "nürnberg", "potsdam", "darmstadt", "mannheim", "münster", "muenster",
    "bonn", "essen", "dortmund", "freiburg", "tübingen", "tuebingen", "jena",
}
DESCRIPTOR = re.compile(
    r"^(?:"
    r"[A-Za-zÄÖÜäöüß][\w.&'’-]*-(?:based|headquartered|founded|born|native)"
    r"|German(?:y(?:'s|’s)?)?|Deutsche[rsn]?|Berlin(?:'s|’s)?"
    r"|[A-ZÄÖÜ][\w.&'’-]*(?:'s|’s)"
    r"|AI|B2B|B2C|SaaS|API|EV|HR|IT"
    r"|fintech|insurtech|proptech|healthtech|biotech|medtech|deeptech|foodtech"
    r"|adtech|agritech|legaltech|edtech|regtech|climate|cleantech|greentech"
    r"|quantum|defence|defense|logistics|mobility|energy|robotics|space"
    r"|crypto|web3|semiconductor|battery|solar|hydrogen|aerospace|drone"
    r"|tech|software|hardware|data|cloud|security|cybersecurity|payments"
    r"|banking|insurance|health|mobile|gaming|retail|industrial|manufacturing"
    r"|startup|start-up|scaleup|scale-up|company|firm|platform|venture|maker"
    r"|developer|provider|specialist|unicorn|group|business|player|outfit"
    r"|Startup|Jungunternehmen|Unternehmen"
    r")\s+", re.I)

# Auxiliaries and adverbs that sit between the name and the verb and would
# otherwise be read as part of the name: "Beispiel has raised", "Beispiel just
# closed", "Beispiel today secures".
TRAILING_FILLER = {
    "has", "have", "had", "just", "also", "now", "today", "again", "hat",
    "haben", "reportedly", "officially", "finally", "successfully", "quietly",
}

# What is left after stripping must still be a name. These are the words that
# most often survive the strip and are not one.
NOT_A_NAME = {
    "the", "a", "an", "this", "it", "they", "he", "she", "we", "you", "and",
    "or", "another", "new", "one", "two", "three", "startup", "company",
    "firm", "founder", "founders", "investor", "investors", "report", "report:",
    "exclusive", "das", "der", "die", "ein", "eine", "einen",
}

# Headlines that are not a closed German round, whatever else they contain.
# A VC closing a fund, a rumour, an acquisition and a listing all match the
# funding vocabulary and none of them is a round.
NOT_A_ROUND = re.compile(
    r"\bin talks\b|\bis raising\b|\bto raise\b|\bseeks?\b|\bseeking\b|"
    r"\bcould\b|\bmay\b|\bmight\b|\breportedly\b|\brumou?red\b|\bplans to\b|"
    r"\bset to\b|\bexpected to\b|\bacquir(?:e|es|ed|ing)\b|\bacquisition\b|"
    r"\bmerger\b|\bmerges\b|\bIPO\b|\bgoes public\b|\blists on\b|"
    r"\binsolven\w*\b|\bshuts? down\b|\blay(?:s|ing)? off\b|"
    r"\b(?:launch(?:es|ed)|clos(?:es|ed)|raises)\b[^.]{0,40}\b(?:fund|vehicle)\b|"
    r"\bfund\s+[IVX]+\b|\bübernimmt\b|\bübernahme\b|\bbörsengang\b",
    re.I)

STAGE = re.compile(r"\b(pre-seed|pre seed|seed|series\s+[a-g])\b", re.I)


def _to_millions(number, scale):
    """"1,2" + "Milliarden" -> 1200.0. A comma with one or two digits behind it
    is a German decimal point; anything else is a thousands separator, which is
    the only reading that makes "1,200 million" and "1,2 Milliarden" both come
    out right."""
    text = number.strip()
    if "," in text and len(text.split(",")[-1]) <= 2 and "." not in text:
        text = text.replace(",", ".")
    else:
        text = text.replace(",", "")
    return round(float(text) * _SCALES[scale.lower()], 4)


def read_amount(text):
    """(amount in millions, currency) from a headline, or None.

    Requires a currency marker *and* a scale word, in either order. Anything
    less is not a figure a reader could check against the page.
    """
    for pattern in (AMOUNT_CURRENCY_FIRST, AMOUNT_CURRENCY_LAST):
        match = pattern.search(text)
        if not match:
            continue
        currency = _CURRENCIES.get(match.group("currency").strip().lower())
        if not currency:
            continue
        try:
            amount = _to_millions(match.group("number"), match.group("scale"))
        except (ValueError, KeyError):
            continue
        if amount > 0:
            return amount, currency
    return None


def read_company(headline):
    """(company, hq) from a headline, or (None, None).

    The company is whatever stands between the publication's own framing and
    the verb: "Berlin-based Beispiel raises …" leaves "Beispiel". The strip is
    conservative in the direction that matters — if what remains does not look
    like a name, this returns None, because a wrong name printed beside a real
    link would send the reader looking for a company that is not there.
    """
    verb = RAISE_VERB.search(headline)
    if not verb:
        return None, None
    candidate = headline[:verb.start()]
    candidate = LEADING_LABEL.sub("", candidate)
    # A publication's own prefix ("Funding news – ") ends at the last dash or
    # colon before the verb; the company is what follows it.
    for separator in (" — ", " – ", " - ", ": ", " | "):
        if separator in candidate:
            candidate = candidate.rsplit(separator, 1)[1]
    candidate = candidate.strip()

    hq = None
    for _ in range(6):                      # bounded: descriptors do not nest deeply
        match = DESCRIPTOR.match(candidate)
        if not match:
            break
        word = match.group(0).strip()
        city = re.split(r"-|'s|’s", word, maxsplit=1)[0].lower()
        if hq is None and city in GERMAN_CITIES:
            hq = word.split("-")[0].split("'")[0].split("’")[0]
        candidate = candidate[match.end():]

    # "Beispiel has raised …", "Beispiel just closed …": the auxiliary belongs
    # to the verb, not to the name, and it arrives on this side of the split.
    candidate = candidate.strip(" ,–—-·|’'\"")
    while True:
        words = candidate.split()
        if words and words[-1].lower() in TRAILING_FILLER:
            candidate = " ".join(words[:-1])
            continue
        break

    candidate = candidate.strip(" ,–—-·|’'\"")
    words = candidate.split()
    if not (1 <= len(words) <= 4) or len(candidate) > 50:
        return None, None
    if not re.search(r"[A-Za-zÄÖÜäöüß0-9]", candidate):
        return None, None
    if candidate.lower() in NOT_A_NAME or words[0].lower() in NOT_A_NAME:
        return None, None
    return candidate, hq


def read_headline(article):
    """One round from one article's headline, or None.

    Every field comes out of `article["title"]`, which is the headline of the
    page whose URL is filed beside it. founders and investors are never read: a
    headline that names them is rare, and this is an annotation on a link, not a
    record. Whoever writes the week takes the figures off the page itself.
    """
    headline = article["title"]
    if NOT_A_ROUND.search(headline):
        return None
    figure = read_amount(headline)
    if not figure:
        return None
    company, hq = read_company(headline)
    if not company:
        return None
    amount, currency = figure
    stage = STAGE.search(headline)
    return {
        "company": company,
        "hq": hq,
        "stage": stage.group(0).title().replace("Pre Seed", "Pre-Seed") if stage else None,
        "amount": amount,
        "currency": currency,
        "approximate": bool(APPROXIMATE_HINT.search(headline)),
    }


# --- the register cross-check ------------------------------------------------

def known_companies(companies_dir="data/companies"):
    """{display name: slug} for everything the register already tracks."""
    directory = pathlib.Path(companies_dir)
    if not directory.is_dir():
        return {}
    known = {}
    for file in sorted(directory.glob("*.json")):
        record = json.loads(file.read_text(encoding="utf-8"))
        known[record["name"]] = record["slug"]
    return known


def tracked_in(text, known):
    """The slug of the tracked company this text names, or None.

    A word-boundary match, borrowed from tools/watch.py rather than rewritten,
    because two copies of "does this headline name a tracked company?" is how
    the two scans start disagreeing about the same headline.
    """
    for name, slug in known.items():
        if _name_pattern(name).search(text):
            return slug
    return None


# --- the week, as the Monday issue needs it ---------------------------------

def candidates(week, feeds=None, fetcher=None, companies_dir="data/companies"):
    """Everything the Monday issue needs about one week, as plain JSON.

    Two buckets, because they earn different attention:

      rounds  the headline reads cleanly as a closed round. This is the list to
              write up.
      other   collected as German funding news, but the headline could not be
              read into a round — a phrasing the parser does not know, a story
              about a round rather than an announcement of one, a fund close.
              Listed anyway: the parser's misses are a person's job to catch,
              and a link costs a line.

    A round for a company already in `data/companies/` carries its slug, because
    that means the register entry is now out of date and the round-up must not
    be the only place the new figure appears.
    """
    articles, errors = collect(week, feeds=feeds, fetcher=fetcher)
    known = known_companies(companies_dir)
    start, end = week_bounds(week)

    rounds, other, seen = [], [], set()
    for article in articles:
        base = {
            "headline": article["title"],
            "publication": article["publication"],
            "publishedOn": article["publishedOn"],
            "url": article["url"],
            "tracked": tracked_in(article["title"], known),
        }
        entry = read_headline(article)
        if entry is None:
            other.append(base)
            continue
        # Two publications covering the same round is the normal case, not a
        # second round. The duplicate is dropped from the list to write up, not
        # from the scan: the second link is often the better-sourced one, so it
        # keeps its place under `other`.
        key = entry["company"].casefold()
        if key in seen:
            other.append(base)
            continue
        seen.add(key)
        rounds.append({**base, **entry,
                       "tracked": base["tracked"] or tracked_in(entry["company"], known)})

    rounds.sort(key=lambda entry: entry["amount"], reverse=True)
    return {
        "week": week,
        "start": start,
        "end": end,
        "scannedOn": dt.date.today().isoformat(),
        "articles": len(articles),
        "feedsTried": len(feeds or FEEDS),
        "feedErrors": errors,
        "rounds": rounds,
        "other": other,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--week", help='ISO week id, e.g. "2026-W30"')
    parser.add_argument("--last-complete-week", action="store_true",
                        help="use the ISO week that ended before --today")
    parser.add_argument("--today", help="YYYY-MM-DD; defaults to the system date")
    parser.add_argument("--report", help="write the candidates here as JSON")
    args = parser.parse_args(argv)

    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    week = args.week or (last_complete_week(today) if args.last_complete_week else None)
    if not week:
        parser.error("pass --week or --last-complete-week")

    report = candidates(week)
    for error in report["feedErrors"]:
        print(f"! feed: {error}", file=sys.stderr)
    print(f"{week} ({report['start']} to {report['end']}): "
          f"{report['articles']} article(s), {len(report['rounds'])} readable round(s)")
    for entry in report["rounds"]:
        mark = f" [tracked: {entry['tracked']}]" if entry["tracked"] else ""
        print(f"- {entry['company']}: {entry['currency']} {entry['amount']}m "
              f"[{entry['publication']}] {entry['url']}{mark}")
    for entry in report["other"]:
        mark = f" [tracked: {entry['tracked']}]" if entry["tracked"] else ""
        print(f"? {entry['headline']} [{entry['publication']}] "
              f"{entry['url']}{mark}")

    if args.report:
        pathlib.Path(args.report).write_text(
            json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    # A quiet week is a real outcome, not a failure. The caller decides whether
    # an empty scan is worth telling anybody about.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
