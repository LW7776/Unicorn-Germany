"""Merges data/companies/*.json into one data/companies.json with everything derived.

Python computes; JavaScript only renders. Every label, sort key, statistic and
staleness flag is settled here so the browser code stays thin and this stays testable.

data/companies.json is committed and CI diffs a freshly generated copy against it, so
the output must be a pure function of the input files: nothing here may read the
wall clock. The "as of" reference used throughout (for staleness and for the
twelve-month window) is derived from the data itself — the latest `publishedOn`
date across every source of every record — not from today's date.

Run: python3 tools/build.py
"""
import json
import pathlib
import statistics
import sys

# Allow `python3 tools/build.py` to resolve `tools.schema` even though running a
# script puts only its own directory on sys.path, not the repo root. pytest is
# unaffected (pytest.ini already puts the repo root on sys.path via pythonpath = .).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools.schema import date_sort_key, format_amount, format_date, parse_date

AGED_AFTER_MONTHS = 24


def _months_between(later, earlier):
    (y1, m1), (y2, m2) = later, earlier
    return (y1 - y2) * 12 + (m1 or 1) - (m2 or 1)


def _to_eur(amount, currency, fx_rate):
    return amount * fx_rate if currency == "USD" else amount


def _data_as_of(records):
    """Latest source publishedOn across every record, as a YYYY-MM-DD string.

    None when there are no records (or no sources) to derive it from — this is
    itself deterministic (a pure function of the, possibly empty, input), never
    a fallback to the wall clock.
    """
    dates = [
        source["publishedOn"]
        for record in records
        for source in record.get("sources", [])
        if source.get("publishedOn")
    ]
    return max(dates) if dates else None


def _year_month(date_str):
    """(year, month) from a YYYY-MM-DD or YYYY-MM string, without touching parse_date's
    stricter YYYY/YYYY-MM-only grammar (publishedOn is a full date)."""
    return int(date_str[0:4]), int(date_str[5:7])


def derive_company(record, today, fx_rate=0.92):
    """today is an as-of reference (year, month) — usually derived from the data's
    own dataAsOf, not the current date. See build()."""
    valuation, rounds = record["valuation"], record["rounds"]
    last_round = rounds[-1] if rounds else None
    unicorn_year, _ = parse_date(record["becameUnicorn"]["date"])
    founders = record.get("founders") or []

    display = {
        "valuationLabel": format_amount(
            valuation["amount"], valuation["currency"], valuation.get("approximate", False)),
        "valuationAsOf": format_date(valuation["asOf"]),
        "lastRoundLabel": format_date(last_round["date"]) if last_round else "—",
        "lastRoundStage": last_round["stage"] if last_round else "—",
        "totalRaisedLabel": format_amount(
            record["totalRaised"]["amount"], record["totalRaised"]["currency"],
            record["totalRaised"].get("approximate", False))
        if record["totalRaised"].get("amount") is not None else "—",
        "yearsToUnicorn": unicorn_year - record["foundedYear"],
        "becameUnicornLabel": format_date(record["becameUnicorn"]["date"]),
        "foundersLabel": ", ".join(f["name"] for f in founders) if founders else "—",
        "aged": _months_between(today, parse_date(valuation["asOf"])) > AGED_AFTER_MONTHS,
    }
    derived_rounds = []
    for entry in rounds:
        derived_rounds.append({
            **entry,
            "dateLabel": format_date(entry["date"]),
            "amountLabel": format_amount(
                entry["amount"], entry["currency"], entry.get("approximate", False))
            if entry.get("amount") is not None else None,
        })
    sort = {
        "newest": list(date_sort_key(record["becameUnicorn"]["date"])),
        # Ordering mixed currencies requires a common unit; this value is a sort key
        # only and is never displayed — display.valuationLabel stays in the source's
        # own currency, so "no FX conversion on a company's own figure" still holds.
        "valuationEur": _to_eur(valuation["amount"], valuation["currency"], fx_rate),
        "latestRound": list(date_sort_key(last_round["date"])) if last_round else [0, 0],
        "name": record["name"].lower(),
    }
    return {**record, "rounds": derived_rounds, "display": display, "sort": sort}


def compute_stats(records, fx):
    rate = fx["USD_EUR"]
    combined = sum(
        _to_eur(r["valuation"]["amount"], r["valuation"]["currency"], rate) for r in records)

    data_as_of = _data_as_of(records)
    recent = 0
    if data_as_of is not None:
        anchor = _year_month(data_as_of)
        for record in records:
            year, month = parse_date(record["becameUnicorn"]["date"])
            months = _months_between(anchor, (year, month))
            if 0 <= months <= 12:
                recent += 1

    years = [r["display"]["yearsToUnicorn"] for r in records]
    return {
        "count": len(records),
        "combinedValuationEurMillions": combined,
        "combinedValuationLabel": format_amount(combined, "EUR", True),
        "newInLast12Months": recent,
        "medianYearsToUnicorn": round(statistics.median(years)) if years else 0,
        "fxRateDisclosed": rate,
        "fxAsOf": fx["asOf"],
        "dataAsOf": data_as_of,
    }


def build(src="data/companies", out="data/companies.json", fx_path="data/fx.json", today=None):
    fx = json.loads(pathlib.Path(fx_path).read_text(encoding="utf-8"))
    raw_records = [
        json.loads(f.read_text(encoding="utf-8"))
        for f in sorted(pathlib.Path(src).glob("*.json"))
    ]

    if today is None:
        # Anchor to the data, never the wall clock: data/companies.json is committed
        # and must be reproducible byte-for-byte on any day CI happens to run.
        data_as_of = _data_as_of(raw_records)
        if data_as_of is None:
            if raw_records:
                raise ValueError("cannot derive dataAsOf: no source carries a publishedOn")
            today = (0, 0)  # unreachable by derive_company: raw_records is empty
        else:
            today = _year_month(data_as_of)

    records = [derive_company(record, today, fx["USD_EUR"]) for record in raw_records]
    payload = {"stats": compute_stats(records, fx), "companies": records}
    out_path = pathlib.Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = build()
    print(f"Built {result['stats']['count']} companies -> data/companies.json")
