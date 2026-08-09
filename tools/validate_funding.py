"""Checks the weekly funding round-up: every round sourced, linked and dated.

Run: python3 tools/validate_funding.py [data/funding]
Exits non-zero and prints every error found.

WHY THIS IS A SEPARATE FILE, NOT PART OF validate.py
----------------------------------------------------
tools/validate.py exists to enforce one promise: every figure in the company
register is backed by a verbatim quote that states that figure. That is the
register's whole claim to trust, and the file is written so the rule cannot be
weakened by accident — quote_states_figure is called on every amount, and there
is no path around it.

The round-up makes a deliberately lighter promise: every round carries a real
source link and a real publication date, and every figure is one a source
states. There is **no quote gate**. Putting a no-quote-required rule inside the
file whose purpose is the quote gate would be one edit away from relaxing the
register itself — the two rule sets would share a namespace, share helpers, and
eventually share a reviewer's assumption about which standard applies where.
Kept apart, neither can be loosened by touching the other, and each can be run
on its own in CI.

What the two files *do* share is tools/schema.py: the source allowlist, the
currency vocabulary and the date grammar. Those are facts about the project, not
about either standard, and duplicating them is how an allowlist drifts.

"Resolvable source URL" is checked structurally — an absolute http(s) URL with a
host — and not by fetching it. A validator that reaches the network is a
validator that fails when a publisher has a bad afternoon, and CI would then
block a correct commit for a reason that has nothing to do with the data.
"""
import datetime as dt
import json
import pathlib
import re
import sys
from urllib.parse import urlparse

# Allow `python3 tools/validate_funding.py` to resolve `tools.schema` even though
# running a script puts only its own directory on sys.path, not the repo root.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools.schema import KNOWN_CURRENCIES, SOURCE_ALLOWLIST, is_full_date

MAX_LEAD = 2
MAX_MORE = 5

WEEK_ID = re.compile(r"^(\d{4})-W(\d{2})$")

# Every key a round may carry, checked by name for the same reason
# validate.py checks ROUND_KEYS by name: a misspelled optional field is
# indistinguishable from an absent one, and silently renders nothing.
ROUND_KEYS = {"id", "company", "hq", "stage", "amount", "currency", "approximate",
              "valuation", "valuationCurrency", "founders", "investors", "source",
              "note"}
LEAD_KEYS = ROUND_KEYS | {"text"}
SOURCE_KEYS = {"publication", "title", "url", "publishedOn"}
WEEK_KEYS = {"week", "start", "end", "lead", "more"}


def _require_string(errors, label, value):
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")


def _require_name_list(errors, label, value):
    """founders and investors are lists — possibly empty. A round whose source
    never named the founders records `[]`, and the renderer omits the clause.
    Inventing the names to fill the owner's sentence template is exactly the
    thing the lighter standard still forbids."""
    if not isinstance(value, list):
        errors.append(f"{label} must be a list (use [] when the source names none)")
        return
    for entry in value:
        if not isinstance(entry, str) or not entry.strip():
            errors.append(f"{label} contains a non-string or empty entry: {entry!r}")


def is_resolvable_url(value):
    """Absolute http(s) with a host. Deliberately not a network fetch — see the
    module docstring. This mirrors the browser-side isSafeUrl check in
    assets/js/html.js, so a URL that passes here is one the renderer will
    actually turn into a link rather than silently downgrading to plain text."""
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = urlparse(value.strip())
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def week_bounds(week_id):
    """(monday, sunday) as YYYY-MM-DD for an ISO week id like "2026-W30".

    Derived, never read off the file: `start` and `end` are then checked against
    this rather than trusted, so a week whose stated range is off by a day
    cannot quietly mis-file a round into the neighbouring week.
    """
    match = WEEK_ID.match(week_id or "")
    if not match:
        raise ValueError(f'week must look like "2026-W30", got {week_id!r}')
    year, week = int(match.group(1)), int(match.group(2))
    try:
        monday = dt.date.fromisocalendar(year, week, 1)
        sunday = dt.date.fromisocalendar(year, week, 7)
    except ValueError as exc:
        raise ValueError(f"{week_id} is not a real ISO week ({exc})") from exc
    return monday.isoformat(), sunday.isoformat()


def _validate_source(errors, label, source, start):
    if not isinstance(source, dict):
        errors.append(f"{label}.source must be an object with "
                      f"publication, title, url and publishedOn")
        return
    for key in sorted(SOURCE_KEYS - set(source)):
        errors.append(f"{label}.source is missing {key}")
    for key in sorted(set(source) - SOURCE_KEYS):
        errors.append(f"{label}.source: unknown field {key!r}")

    publication = source.get("publication")
    if publication not in SOURCE_ALLOWLIST:
        errors.append(
            f"{label}.source publication not on the allowlist: {publication!r} "
            f"— the round-up draws on the same allowlist as the register "
            f"(tools/schema.py)")
    _require_string(errors, f"{label}.source.title", source.get("title"))

    if not is_resolvable_url(source.get("url")):
        errors.append(
            f"{label}.source.url must be an absolute http(s) URL a reader can "
            f"open: {source.get('url')!r}")

    published = source.get("publishedOn")
    if not is_full_date(published):
        errors.append(
            f"{label}.source.publishedOn must be a real YYYY-MM-DD publication "
            f"date, got {published!r}")
    elif published < start:
        # A round cannot be reported before the week it happened in. Coverage
        # *after* the week is ordinary and allowed — a Friday round routinely
        # lands in the following Monday's weekly recap — so only the
        # impossible direction is an error.
        errors.append(
            f"{label}.source.publishedOn ({published}) predates the week it is "
            f"filed under (starts {start}) — this round belongs in an earlier week")


def _validate_round(errors, label, entry, start, is_lead):
    if not isinstance(entry, dict):
        errors.append(f"{label} must be an object")
        return
    allowed = LEAD_KEYS if is_lead else ROUND_KEYS
    for key in sorted(set(entry) - allowed):
        if key == "text" and not is_lead:
            errors.append(
                f"{label}: `more` rounds are listed, not written up — move this "
                f"entry into `lead` or delete its `text`")
        else:
            errors.append(
                f"{label}: unknown field {key!r} — a misspelled optional field "
                f"is silently ignored, so it is rejected by name")

    _require_string(errors, f"{label}.id", entry.get("id"))
    _require_string(errors, f"{label}.company", entry.get("company"))

    # hq and stage are optional context: a weekly recap line often gives a
    # figure and a country and nothing else. Absent is honest; wrong is not.
    for optional in ("hq", "stage"):
        value = entry.get(optional)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            errors.append(f"{label}.{optional} must be a non-empty string or null")

    amount = entry.get("amount")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        errors.append(f"{label}.amount must be a number of millions, got {amount!r}")
    elif amount <= 0:
        errors.append(f"{label}.amount must be greater than zero, got {amount!r}")

    currency = entry.get("currency")
    if currency not in KNOWN_CURRENCIES:
        errors.append(
            f"{label}.currency is not a currency this site can render: "
            f"{currency!r} (known: {', '.join(sorted(KNOWN_CURRENCIES))})")

    approximate = entry.get("approximate")
    if not isinstance(approximate, bool):
        errors.append(f"{label}.approximate must be true or false")

    valuation = entry.get("valuation")
    valuation_currency = entry.get("valuationCurrency")
    if valuation is not None:
        if isinstance(valuation, bool) or not isinstance(valuation, (int, float)):
            errors.append(f"{label}.valuation must be a number of millions or null")
        elif valuation <= 0:
            errors.append(f"{label}.valuation must be greater than zero")
        if valuation_currency not in KNOWN_CURRENCIES:
            errors.append(
                f"{label}.valuationCurrency is required alongside a valuation and "
                f"must be one of {', '.join(sorted(KNOWN_CURRENCIES))}, got "
                f"{valuation_currency!r}")
    elif valuation_currency is not None:
        errors.append(
            f"{label}.valuationCurrency is set but valuation is null — a currency "
            f"with no figure under it is a label for nothing")

    _require_name_list(errors, f"{label}.founders", entry.get("founders"))
    _require_name_list(errors, f"{label}.investors", entry.get("investors"))

    if is_lead:
        text = entry.get("text")
        if not isinstance(text, str) or not text.strip():
            errors.append(
                f"{label}.text must be a non-empty write-up — a lead round without "
                f"prose is an additional round; move it to `more`")

    _validate_source(errors, label, entry.get("source"), start)
    _validate_note(errors, label, entry.get("note"), start)


def _validate_note(errors, label, note, start):
    """A second, conflicting figure for the same round, recorded rather than
    reconciled.

    Sources disagree about a round more often than is comfortable: a company
    announces €35m and the trade press reports €30m, because they are counting
    different things or working from different briefings. The register already
    settled how to handle that — publish the company's own figure for its own
    round, and record the disagreement beside it with its own citation — and the
    round-up has to reach the same answer, or the same site states two different
    numbers for one round and a reader concludes something is broken.

    So a note is not free text. It carries its own source, checked exactly like
    the round's: allowlisted, dated, and a URL a reader can open. The whole point
    is that the *other* figure is as traceable as the published one.
    """
    if note is None:
        return
    if not isinstance(note, dict):
        errors.append(f"{label}.note must be an object with text and source")
        return
    for key in sorted({"text", "source"} - set(note)):
        errors.append(f"{label}.note is missing {key}")
    for key in sorted(set(note) - {"text", "source"}):
        errors.append(f"{label}.note: unknown field {key!r}")
    _require_string(errors, f"{label}.note.text", note.get("text"))
    if "source" in note:
        _validate_source(errors, f"{label}.note", note.get("source"), start)


def validate_week(record):
    errors = []

    for key in sorted(WEEK_KEYS - set(record)):
        errors.append(f"missing required field: {key}")
    for key in sorted(set(record) - WEEK_KEYS):
        errors.append(f"unknown field {key!r}")
    if errors:
        return errors

    try:
        start, end = week_bounds(record["week"])
    except ValueError as exc:
        return [str(exc)]

    if record["start"] != start:
        errors.append(
            f"start must be the Monday of {record['week']} ({start}), got "
            f"{record['start']!r}")
    if record["end"] != end:
        errors.append(
            f"end must be the Sunday of {record['week']} ({end}), got "
            f"{record['end']!r}")

    lead, more = record["lead"], record["more"]
    if not isinstance(lead, list):
        errors.append("lead must be a list")
        return errors
    if not isinstance(more, list):
        errors.append("more must be a list")
        return errors

    if not lead:
        errors.append("lead must carry at least one written-up round")
    elif len(lead) > MAX_LEAD:
        errors.append(
            f"lead carries {len(lead)} rounds; at most {MAX_LEAD} are written up "
            f"in a week — move the rest to `more`")
    if len(more) > MAX_MORE:
        errors.append(
            f"more carries {len(more)} rounds; the cap is {MAX_MORE} so a week "
            f"stays readable — drop the smallest, or promote one to `lead`")

    for index, entry in enumerate(lead):
        _validate_round(errors, f"lead[{index}]", entry, start, is_lead=True)
    for index, entry in enumerate(more):
        _validate_round(errors, f"more[{index}]", entry, start, is_lead=False)

    seen = {}
    for group, entries in (("lead", lead), ("more", more)):
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            entry_id = entry.get("id")
            if not isinstance(entry_id, str):
                continue
            where = f"{group}[{index}]"
            if entry_id in seen:
                errors.append(
                    f"{where}: duplicate id {entry_id!r} (also {seen[entry_id]}) "
                    f"— ids key the rendered list, so a repeat collides")
            else:
                seen[entry_id] = where
    return errors


def validate_directory(path="data/funding"):
    results = {}
    directory = pathlib.Path(path)
    if not directory.is_dir():
        return {path: [f"{path} is not a directory"]}
    for file in sorted(directory.glob("*.json")):
        record = json.loads(file.read_text(encoding="utf-8"))
        errors = validate_week(record)
        if record.get("week") != file.stem:
            errors.append(
                f"week {record.get('week')!r} does not match filename {file.stem!r}")
        if errors:
            results[file.stem] = errors
    return results


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "data/funding"
    results = validate_directory(target)
    for week, errors in results.items():
        for error in errors:
            print(f"{week}: {error}")
    count = sum(len(v) for v in results.values())
    print(f"{count} error(s) across {len(results)} file(s)" if count
          else "All funding weeks valid.")
    return 1 if count else 0


if __name__ == "__main__":
    raise SystemExit(main())
