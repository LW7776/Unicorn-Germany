"""Refuses to publish a figure that is not backed by a dated, quoted, allowlisted source.

Run: python3 tools/validate.py [data/companies]
Exits non-zero and prints every error found.
"""
import json
import pathlib
import re
import sys

from tools.schema import (
    SOURCE_ALLOWLIST, date_sort_key, is_full_date, parse_date, quote_states_figure,
)

REQUIRED = ["slug", "name", "website", "logo", "hq", "foundedCountry", "foundedYear",
            "sectors", "thesis", "valuation", "becameUnicorn", "totalRaised",
            "rounds", "founders", "investors", "sources"]
THRESHOLD_MILLIONS = 1000          # $1B or €1B, as reported. No FX conversion.
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_company(record):
    errors = []
    for field in REQUIRED:
        if field not in record:
            errors.append(f"missing required field: {field}")
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
                f"{label}: quote for source {source_id} does not contain the figure {amount}")

    check_figure("valuation", record["valuation"])
    check_figure("totalRaised", record["totalRaised"])

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

    by_id = {entry.get("id"): entry for entry in rounds}
    unicorn_round = by_id.get(record["becameUnicorn"].get("roundId"))
    if unicorn_round is None:
        errors.append(
            f"becameUnicorn.roundId {record['becameUnicorn'].get('roundId')!r} matches no round")
    elif (unicorn_round.get("postMoney") or 0) < THRESHOLD_MILLIONS:
        errors.append(
            f"round {unicorn_round['id']} post-money is below the "
            f"{THRESHOLD_MILLIONS}m inclusion threshold")

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
