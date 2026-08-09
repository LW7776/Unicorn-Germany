"""Drafts one week of the funding round-up from the allowlisted feeds.

Run: python3 tools/weekly_funding.py --week 2026-W30 [--out data/funding]
     python3 tools/weekly_funding.py --last-complete-week --today 2026-08-10

It fetches the feeds tools/watch.py already knows how to fetch, keeps the items
published inside the week, asks Claude to pick the lead round(s) and write them
up, and then — before anything is written — checks the model's answer back
against the fetched text. The result is a draft for a human to read in a pull
request. Nothing here commits, and nothing here publishes.

THE THREE GUARDS
----------------
The prompt forbids inventing a company, a figure or a founder. A prompt is a
request, so two checks in code make it a rule:

  1. Every round's source URL must be one the fetch actually returned. A model
     cannot cite a page this run never saw, because the URL is looked up in the
     corpus rather than trusted.
  2. Every company name, founder name and amount must appear in *that article's*
     text. A figure the article does not contain cannot be filed against it,
     which is what stops a plausible number being attached to a real link.
  3. tools/validate_funding.py runs afterwards on the written file, in CI, and
     the workflow refuses to open a pull request if it fails.

Guard 2 is the load-bearing one. It is deliberately a substring test over the
article body rather than a judgement about meaning: it cannot tell whether the
model understood the round, but it can tell — mechanically, with no model in the
loop — that every proper noun and every number came from the page that is cited
beside it.
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools.schema import SOURCE_ALLOWLIST, quote_states_figure
from tools.validate_funding import MAX_LEAD, MAX_MORE, validate_week, week_bounds
from tools.watch import FEEDS, fetch, parse_feed

MODEL = "claude-opus-5"
MAX_TOKENS = 16000
# How many articles to put in front of the model. The feeds return far more
# than a week's German funding news, and the filter below is deliberately
# permissive — better to hand over a few irrelevant articles than to filter out
# the one round that mattered with a regex.
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
# the model, the checks below, and the person reading the pull request — the
# same division of labour tools/watch.py already documents for its own scan.
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

SYSTEM = """You compile a weekly round-up of German company funding rounds for a \
public register that is read as a factual record.

You will be given the full text of articles from allowlisted trade publications, \
each with an id, a publication, a URL and a publication date. That material is \
the ONLY thing you may draw on.

ABSOLUTE RULES — these are not style preferences:
- Never state a company, a founder, an investor, an amount, a valuation, a \
funding stage or a date that does not appear in the supplied articles. If it is \
not in the material, it does not exist for this task.
- Never carry anything over from your own knowledge of these companies, however \
confident you are. Your training data is not a source.
- Every round must cite the id of the ONE supplied article that states it.
- If an article does not name the founders, return an empty founders list. Do \
not fill the gap. An omission is correct; a guess is a defect.
- If an article gives no valuation, leave the valuation null. Do not infer one \
from the amount raised, and never divide or multiply your way to a figure.
- Amounts are in millions of the stated currency: €13.1 million is 13.1 with \
currency EUR; $1.2 billion is 1200 with currency USD. Only EUR and USD may be \
used; if a round is reported in another currency, omit the round entirely.
- Only include companies the material describes as German or headquartered in \
Germany. If nationality is unclear, omit the round.
- Only include closed, announced rounds. Omit rounds described as "in talks", \
"could soon announce", "is raising", or otherwise unconfirmed.
- Omit acquisitions, IPOs, fund closes by VC firms, and rounds with no \
disclosed amount.

SELECTION:
- Choose 1 or 2 lead rounds — 1 unless a second genuinely deserves the space — \
and write each up in one paragraph.
- List up to 5 further rounds with no prose. If more than 5 qualify, keep the \
largest by amount raised.

THE WRITE-UPS:
Write like a well-informed, confident correspondent who thinks the German \
ecosystem is underrated and says so. State the round, then why it matters. \
Concrete and specific; no hype adjectives, no "poised to disrupt", no exclamation \
marks. Roughly 60-110 words each.
The prose must age well. Never write a flat, down or bridge round as a triumph. \
Never write a superlative you cannot support from the supplied material — "the \
ninth in twelve months" is usable only if the material lets you count it. If you \
are tempted to claim a company is the biggest, first or fastest at something, \
either quote the article that says so and attribute it, or drop the claim."""

SCHEMA = {
    "type": "object",
    "properties": {
        "lead": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "hq": {"type": ["string", "null"]},
                    "stage": {"type": ["string", "null"]},
                    "amount": {"type": "number"},
                    "currency": {"type": "string", "enum": ["EUR", "USD"]},
                    "approximate": {"type": "boolean"},
                    "valuation": {"type": ["number", "null"]},
                    "valuationCurrency": {"type": ["string", "null"],
                                          "enum": ["EUR", "USD", None]},
                    "founders": {"type": "array", "items": {"type": "string"}},
                    "investors": {"type": "array", "items": {"type": "string"}},
                    "text": {"type": "string"},
                    "articleId": {"type": "string"},
                },
                "required": ["company", "hq", "stage", "amount", "currency",
                             "approximate", "valuation", "valuationCurrency",
                             "founders", "investors", "text", "articleId"],
                "additionalProperties": False,
            },
        },
        "more": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "hq": {"type": ["string", "null"]},
                    "stage": {"type": ["string", "null"]},
                    "amount": {"type": "number"},
                    "currency": {"type": "string", "enum": ["EUR", "USD"]},
                    "approximate": {"type": "boolean"},
                    "valuation": {"type": ["number", "null"]},
                    "valuationCurrency": {"type": ["string", "null"],
                                          "enum": ["EUR", "USD", None]},
                    "founders": {"type": "array", "items": {"type": "string"}},
                    "investors": {"type": "array", "items": {"type": "string"}},
                    "articleId": {"type": "string"},
                },
                "required": ["company", "hq", "stage", "amount", "currency",
                             "approximate", "valuation", "valuationCurrency",
                             "founders", "investors", "articleId"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["lead", "more"],
    "additionalProperties": False,
}


# --- collecting -------------------------------------------------------------

def last_complete_week(today):
    """The ISO week that ended before `today`. Monday's run covers the week just
    finished, not the one it is standing in. `today` is passed in rather than
    read from the clock so this is testable and so the workflow can be replayed
    for a past week."""
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
    # Longest first: an article with the full body is far more useful to both
    # the model and the verifier than a headline-only stub, and the cap has to
    # fall on the stubs rather than on whichever feed happened to be polled last.
    articles.sort(key=lambda a: len(a["text"]), reverse=True)
    return articles[:MAX_ARTICLES], errors


# --- the model call ---------------------------------------------------------

def build_prompt(week, articles):
    start, end = week_bounds(week)
    lines = [
        f"ISO week {week}: {start} to {end} inclusive.",
        f"{len(articles)} articles follow. Draw only on these.",
        "",
    ]
    for article in articles:
        lines += [
            f"<article id=\"{article['id']}\">",
            f"publication: {article['publication']}",
            f"published: {article['publishedOn']}",
            f"url: {article['url']}",
            f"headline: {article['title']}",
            "",
            article["text"] or "(no body text in the feed; use the headline only)",
            "</article>",
            "",
        ]
    lines.append(
        f"Return the lead round(s) (at most {MAX_LEAD}) and up to {MAX_MORE} "
        f"further rounds, each citing the id of the single article that states it.")
    return "\n".join(lines)


def draft(week, articles, client=None):
    """Ask Claude to select and write the week. Returns the parsed JSON object."""
    if client is None:
        import anthropic
        client = anthropic.Anthropic()          # reads ANTHROPIC_API_KEY

    # Streaming, because the article corpus can run to tens of thousands of
    # tokens and a non-streaming request at this max_tokens risks an HTTP
    # timeout well before the model is finished.
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM,
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": build_prompt(week, articles)}],
    ) as stream:
        message = stream.get_final_message()

    if message.stop_reason == "refusal":
        raise RuntimeError(
            "the model declined this request; nothing was written "
            f"({getattr(message, 'stop_details', None)})")
    if message.stop_reason == "max_tokens":
        raise RuntimeError(
            "the model hit max_tokens, so the JSON is truncated; nothing was written")

    text = next((b.text for b in message.content if b.type == "text"), "")
    return json.loads(text)


# --- verifying the draft against the fetched text ---------------------------

def states_figure(text, amount, currency):
    """Does this article state this figure, in this currency?

    Delegates to tools/schema.py's matcher — the same one the register's quote
    gate uses. Reusing it is not incidental: a hand-rolled substring test gets
    this wrong in a way that is easy to miss. A €1bn valuation is stored as
    1000, whose billions form is the bare string "1", and "1" is a substring of
    "2021" and of "€12 million" — so a naive check waves through an invented
    billion-euro valuation on any article that happens to mention a year.
    quote_states_figure matches on digit boundaries and additionally requires a
    scale word beside a billion-scale figure, which is exactly the distinction
    that matters here.

    This is emphatically *not* the register's quote gate. Nothing about the
    round-up requires a verbatim quote in the data file, and none is stored.
    This is an internal check on the model's output, and it is only ever run
    against the article the model itself cited.
    """
    return quote_states_figure(text, amount, currency)


def verify(rounds, articles):
    """Every claim traced back to the article cited beside it.

    Returns a list of problems. An empty list means every company, founder and
    figure in the draft is a substring of the page it is filed against.
    """
    by_id = {article["id"]: article for article in articles}
    problems = []
    for entry in rounds:
        label = entry.get("company") or "?"
        article = by_id.get(entry.get("articleId"))
        if article is None:
            problems.append(
                f"{label}: cites article {entry.get('articleId')!r}, which this "
                f"run never fetched — the model may have invented the citation")
            continue
        body = f"{article['title']} {article['text']}"
        haystack = body.lower()

        if entry["company"].lower() not in haystack:
            problems.append(
                f"{label}: the company name does not appear in {article['url']}")
        for founder in entry.get("founders") or []:
            # Surname is enough: articles routinely introduce "Dr. Denis Kiefel"
            # and then say "Kiefel", and a full-string test would reject a
            # correctly-extracted name over a title or a middle initial.
            surname = founder.split()[-1].lower()
            if surname not in haystack:
                problems.append(
                    f"{label}: founder {founder!r} does not appear in {article['url']}")
        if not states_figure(body, entry["amount"], entry["currency"]):
            problems.append(
                f"{label}: {article['url']} does not state the amount "
                f"{entry['amount']} in {entry['currency']}")
        valuation = entry.get("valuation")
        if valuation is not None and not states_figure(
                body, valuation, entry.get("valuationCurrency") or entry["currency"]):
            problems.append(
                f"{label}: {article['url']} does not state the valuation "
                f"{valuation} in {entry.get('valuationCurrency') or entry['currency']}")
    return problems


# --- assembling the week file ----------------------------------------------

def assemble(week, drafted, articles):
    """Turn the model's answer into the on-disk shape, resolving article ids to
    real source objects. The model never writes a URL or a publication name —
    it names an article, and those fields are copied from what was fetched, so
    a citation cannot drift from the page it came from."""
    start, end = week_bounds(week)
    by_id = {article["id"]: article for article in articles}

    def convert(entry, index, prefix, with_text):
        article = by_id[entry["articleId"]]
        out = {
            "id": f"{prefix}{index + 1}",
            "company": entry["company"],
            "hq": entry.get("hq") or None,
            "stage": entry.get("stage") or None,
            "amount": entry["amount"],
            "currency": entry["currency"],
            "approximate": bool(entry.get("approximate")),
            "valuation": entry.get("valuation"),
            "valuationCurrency": entry.get("valuationCurrency"),
            "founders": entry.get("founders") or [],
            "investors": entry.get("investors") or [],
            "source": {
                "publication": article["publication"],
                "title": article["title"],
                "url": article["url"],
                "publishedOn": article["publishedOn"],
            },
        }
        if with_text:
            out["text"] = entry["text"]
        return out

    return {
        "week": week,
        "start": start,
        "end": end,
        "lead": [convert(e, i, "l", True) for i, e in enumerate(drafted["lead"])],
        "more": [convert(e, i, "m", False) for i, e in enumerate(drafted["more"])],
    }


def tracked_companies(week_record, companies_dir="data/companies"):
    """Companies in this week that the register already tracks.

    Surfaced prominently in the pull request: a round for a company already in
    the register means the register entry is now out of date, and the round-up
    is not allowed to be the only place that new figure appears.
    """
    directory = pathlib.Path(companies_dir)
    if not directory.is_dir():
        return []
    known = {}
    for file in sorted(directory.glob("*.json")):
        record = json.loads(file.read_text(encoding="utf-8"))
        known[record["name"].lower()] = record["slug"]
    hits = []
    for entry in week_record["lead"] + week_record["more"]:
        slug = known.get(entry["company"].lower())
        if slug:
            hits.append({"company": entry["company"], "slug": slug,
                         "amount": entry["amount"], "currency": entry["currency"],
                         "source": entry["source"]["url"]})
    return hits


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week", help='ISO week id, e.g. "2026-W30"')
    parser.add_argument("--last-complete-week", action="store_true",
                        help="use the ISO week that ended before --today")
    parser.add_argument("--today", help="YYYY-MM-DD; defaults to the system date")
    parser.add_argument("--out", default="data/funding")
    parser.add_argument("--report", help="write a JSON run report here (for the PR body)")
    args = parser.parse_args(argv)

    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    week = args.week or (last_complete_week(today) if args.last_complete_week else None)
    if not week:
        parser.error("pass --week or --last-complete-week")

    articles, errors = collect(week)
    for error in errors:
        print(f"! feed: {error}", file=sys.stderr)
    print(f"{len(articles)} candidate article(s) for {week}")
    if not articles:
        # A genuinely quiet week is a real outcome, not a failure — but there is
        # nothing to publish and nothing to review, so stop before spending an
        # API call and before opening an empty pull request.
        print("nothing to draft; no file written")
        return 2

    drafted = draft(week, articles)
    problems = verify(drafted["lead"] + drafted["more"], articles)
    if problems:
        for problem in problems:
            print(f"! unverified: {problem}", file=sys.stderr)
        print("draft rejected: a claim could not be traced to the article cited "
              "for it; no file written", file=sys.stderr)
        return 1

    record = assemble(week, drafted, articles)
    validation = validate_week(record)
    if validation:
        for error in validation:
            print(f"! invalid: {error}", file=sys.stderr)
        print("draft rejected: it does not satisfy tools/validate_funding.py; "
              "no file written", file=sys.stderr)
        return 1

    out_path = pathlib.Path(args.out) / f"{week}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    print(f"wrote {out_path}: {len(record['lead'])} lead, {len(record['more'])} listed")

    if args.report:
        tracked = tracked_companies(record)
        pathlib.Path(args.report).write_text(json.dumps({
            "week": week,
            "articles": len(articles),
            "feedErrors": errors,
            "lead": [{"company": e["company"], "amount": e["amount"],
                      "currency": e["currency"], "url": e["source"]["url"],
                      "publishedOn": e["source"]["publishedOn"]}
                     for e in record["lead"]],
            "more": [{"company": e["company"], "amount": e["amount"],
                      "currency": e["currency"], "url": e["source"]["url"],
                      "publishedOn": e["source"]["publishedOn"]}
                     for e in record["more"]],
            "tracked": tracked,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
