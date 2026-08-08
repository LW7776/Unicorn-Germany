"""Refuses to publish a figure that is not backed by a dated, quoted, allowlisted source.

Run: python3 tools/validate.py [data/companies]
Exits non-zero and prints every error found.

assets/js/admin.js mirrors the rules below in the browser, so the operator filling in the
form editor sees errors while typing instead of after committing. This file remains the sole
authority and the only gate that can block a publish — rebuild.yml runs it before
tools/build.py ever touches data/companies.json, and .github/workflows/validate.yml runs it
on every push and pull request. If the two ever disagree, CI catches it here and the
published site is never wrong; the browser copy can only be over- or under-helpful, never
dangerous. This duplication is deliberate, not an oversight — see the matching comment at the
top of assets/js/admin.js.
"""
import json
import pathlib
import re
import sys

# Allow `python3 tools/validate.py` to resolve `tools.schema` even though running a
# script puts only its own directory on sys.path, not the repo root. pytest is
# unaffected (pytest.ini already puts the repo root on sys.path via pythonpath = .).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools.schema import (
    SOURCE_ALLOWLIST, date_sort_key, is_full_date, parse_date, quote_states_figure,
)

REQUIRED = ["slug", "name", "website", "logo", "hq", "foundedCountry", "foundedYear",
            "sectors", "thesis", "valuation", "becameUnicorn", "totalRaised",
            "rounds", "founders", "investors", "sources"]
THRESHOLD_MILLIONS = 1000          # $1B or €1B, as reported. No FX conversion.
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _require_string(errors, label, value):
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")


def _validate_types(record):
    """Presence (REQUIRED, above) only proves a key exists — a record can pass
    that check with `"sectors": null` or `"foundedYear": "2015"` and still
    crash every consumer downstream (the browser's `flatMap`, this file's own
    figure checks, tools/build.py's derive_company). This is the real gate:
    it fails fast, before any code assumes a field has the shape it needs."""
    errors = []
    for label, key in (("name", "name"), ("website", "website"),
                        ("logo", "logo"), ("slug", "slug")):
        _require_string(errors, label, record.get(key))

    sectors = record.get("sectors")
    if not isinstance(sectors, list) or not sectors:
        errors.append("sectors must be a non-empty list")
    else:
        for entry in sectors:
            if not isinstance(entry, str) or not entry.strip():
                errors.append(f"sectors contains a non-string or empty entry: {entry!r}")

    hq = record.get("hq")
    if not isinstance(hq, dict):
        errors.append("hq must be an object with city and country")
    else:
        _require_string(errors, "hq.city", hq.get("city"))
        _require_string(errors, "hq.country", hq.get("country"))

    # Optional: dual-HQ cases (Celonis is Munich and New York, for example)
    # recorded explicitly rather than forced into the single `hq` object.
    also_based_in = record.get("alsoBasedIn")
    if also_based_in is not None:
        if not isinstance(also_based_in, list):
            errors.append("alsoBasedIn must be a list of non-empty strings")
        else:
            for entry in also_based_in:
                if not isinstance(entry, str) or not entry.strip():
                    errors.append(
                        f"alsoBasedIn contains a non-string or empty entry: {entry!r}")

    for field in ("founders", "investors", "rounds", "sources"):
        if not isinstance(record.get(field), list):
            errors.append(f"{field} must be a list")

    founded_year = record.get("foundedYear")
    if not isinstance(founded_year, int) or isinstance(founded_year, bool):
        errors.append("foundedYear must be an integer")

    return errors


def validate_company(record):
    errors = []
    for field in REQUIRED:
        if field not in record:
            errors.append(f"missing required field: {field}")
    if errors:
        return errors

    errors = _validate_types(record)
    if errors:
        return errors

    if not SLUG.match(record["slug"]):
        errors.append(f"slug must be lowercase and hyphenated: {record['slug']!r}")
    if not str(record["website"]).startswith("https://"):
        errors.append("website must be an https URL")

    sources = {}
    for source in record["sources"]:
        for field in ("id", "publication", "title", "url", "publishedOn", "quote"):
            if not source.get(field):
                errors.append(f"source {source.get('id', '?')} is missing {field}")
        if source.get("publication") not in SOURCE_ALLOWLIST:
            errors.append(f"source publication not on the allowlist: {source.get('publication')!r}")
        if not is_full_date(source.get("publishedOn", "")):
            errors.append(
                f"source {source.get('id')} publishedOn must be a real YYYY-MM-DD publication date")
        sources[source.get("id")] = source

    def check_figure(label, figure, amount_key="amount"):
        source_id = figure.get("source")
        if source_id not in sources:
            errors.append(f"{label} cites unknown source {source_id!r}")
            return
        amount = figure.get(amount_key)
        if amount is None:
            return
        if not quote_states_figure(
                sources[source_id]["quote"], amount, figure.get("currency")):
            errors.append(
                f"{label}: quote for source {source_id} does not state the figure {amount} "
                f"and its currency — extend the quote to a sentence naming both")

    def check_disputed(label, container):
        """A conflicting figure recorded alongside the one on file, so the site never
        silently picks one on the reader's behalf. Optional, and shaped and
        source-checked identically wherever it appears — on `valuation`, and on any
        round whose amount the sources disagree about."""
        disputed = container.get("disputed")
        if disputed is None:
            return
        if not isinstance(disputed, dict):
            errors.append(f"{label}.disputed must be an object with note and source")
            return
        note = disputed.get("note")
        if not isinstance(note, str) or not note.strip():
            errors.append(f"{label}.disputed.note must be a non-empty string")
        if disputed.get("source") not in sources:
            errors.append(
                f"{label}.disputed cites unknown source {disputed.get('source')!r}")

    check_figure("valuation", record["valuation"])
    check_figure("totalRaised", record["totalRaised"])
    check_disputed("valuation", record["valuation"])

    for field, value in (("valuation.asOf", record["valuation"].get("asOf")),
                         ("becameUnicorn.date", record["becameUnicorn"].get("date"))):
        try:
            parse_date(value)
        except ValueError as exc:
            errors.append(f"{field}: {exc}")

    rounds, previous = record["rounds"], None
    for entry in rounds:
        try:
            key = date_sort_key(entry["date"])
        except (ValueError, KeyError) as exc:
            errors.append(f"round {entry.get('id')}: bad date ({exc})")
            continue
        if previous is not None and key < previous:
            errors.append(f"rounds must be in chronological order: {entry['id']} is out of order")
        previous = key
        check_figure(f"round {entry['id']}", entry)
        check_figure(f"round {entry['id']} post-money", entry, amount_key="postMoney")
        check_disputed(f"round {entry['id']}", entry)

    by_id = {entry.get("id"): entry for entry in rounds}
    unicorn_round = by_id.get(record["becameUnicorn"].get("roundId"))
    if unicorn_round is None:
        errors.append(
            f"becameUnicorn.roundId {record['becameUnicorn'].get('roundId')!r} matches no round")
    elif (unicorn_round.get("postMoney") or 0) < THRESHOLD_MILLIONS:
        errors.append(
            f"round {unicorn_round['id']} post-money is below the "
            f"{THRESHOLD_MILLIONS}m inclusion threshold")
    else:
        # A record can be internally consistent and still name the wrong round: every
        # figure sourced, every quote honest, and becameUnicorn pointing at a later
        # round than the one that actually crossed. Nothing above catches that, because
        # nothing above compares the rounds to each other — and the error escapes into
        # published derived figures (yearsToUnicorn, the "crossed €1bn" flag, the
        # newest-unicorn sort). If an earlier round already carries a post-money at or
        # above the threshold, the company crossed there.
        try:
            unicorn_key = date_sort_key(unicorn_round["date"])
        except (ValueError, KeyError):
            unicorn_key = None
        if unicorn_key is not None:
            for entry in rounds:
                if entry is unicorn_round or (entry.get("postMoney") or 0) < THRESHOLD_MILLIONS:
                    continue
                try:
                    if date_sort_key(entry["date"]) >= unicorn_key:
                        continue
                except (ValueError, KeyError):
                    continue
                errors.append(
                    f"round {entry['id']} ({entry['date']}) already has a post-money at or above "
                    f"the {THRESHOLD_MILLIONS}m threshold, so becameUnicorn cannot be round "
                    f"{unicorn_round['id']} ({unicorn_round['date']}) — the company crossed earlier")

    if rounds:
        try:
            if date_sort_key(record["valuation"]["asOf"]) < date_sort_key(rounds[-1]["date"]):
                errors.append("valuation.asOf predates the most recent round")
        except ValueError:
            pass
    return errors


def validate_directory(path="data/companies"):
    results = {}
    for file in sorted(pathlib.Path(path).glob("*.json")):
        record = json.loads(file.read_text(encoding="utf-8"))
        errors = validate_company(record)
        if record.get("slug") != file.stem:
            errors.append(f"slug {record.get('slug')!r} does not match filename {file.stem!r}")
        if errors:
            results[file.stem] = errors
    return results


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "data/companies"
    results = validate_directory(target)
    for slug, errors in results.items():
        for error in errors:
            print(f"{slug}: {error}")
    count = sum(len(v) for v in results.values())
    print(f"{count} error(s) across {len(results)} file(s)" if count else "All records valid.")
    return 1 if count else 0


if __name__ == "__main__":
    raise SystemExit(main())
