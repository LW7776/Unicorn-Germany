"""Merges the per-record source files into the two JSON payloads the site fetches.

data/companies/*.json -> data/companies.json  (the register)
data/funding/*.json   -> data/funding.json    (the weekly round-up)

Python computes; JavaScript only renders. Every label, sort key, statistic and
staleness flag is settled here so the browser code stays thin and this stays testable.

Both outputs are committed and CI diffs freshly generated copies against them, so
each must be a pure function of its input files: nothing here may read the
wall clock. The "as of" reference used throughout (for staleness and for the
twelve-month window) is derived from the data itself — the latest `publishedOn`
date across every source of every record — not from today's date. The round-up
orders itself by ISO week id, which is likewise in the data.

The funding build lives here rather than in a sibling script so that
`python3 tools/build.py` remains the one build command: rebuild.yml and
validate.yml already run it, so neither generated file can go stale because
somebody added a second command and a workflow forgot it.

Run: python3 tools/build.py
"""
import json
import pathlib
import statistics
import sys
from decimal import Decimal, ROUND_HALF_UP

# Allow `python3 tools/build.py` to resolve `tools.schema` even though running a
# script puts only its own directory on sys.path, not the repo root. pytest is
# unaffected (pytest.ini already puts the repo root on sys.path via pythonpath = .).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools.schema import (
    CURRENCY_SYMBOL, MONTHS, date_sort_key, format_amount, format_date, parse_date)

# When a valuation earns the "aged" marker.
#
# The old rule was a single 24-month age test, and it fired on 15 of 32 records —
# nearly half the register, which turns a warning into wallpaper. It also flagged
# something the page already says out loud: every valuation prints "as of Aug 2022"
# right beside itself, so plain age is disclosed whether or not a badge repeats it.
#
# The marker now means the narrower and more useful thing: the register has positive
# reason to believe this figure has been overtaken.
#
#   AGED_BEHIND_ROUND_MONTHS  The company has raised money more than two years after
#                             the last published valuation and nobody restated the
#                             price. (validate.py already rejects the case where that
#                             later round *did* disclose a post-money — then the newer
#                             figure is the one on file.) Two years is well past the
#                             point where a round leaves the headline behind.
#   AGED_AFTER_MONTHS         A five-year backstop for a company that has been quiet
#                             throughout. At that distance the figure cannot be relied
#                             on however little has happened. Four years was tested and
#                             still flagged 11 of 32, which is not a signal.
#
# Against the shipped dataset the pair flags 4 of 32.
AGED_AFTER_MONTHS = 60
AGED_BEHIND_ROUND_MONTHS = 24

# What the grid card and the detail window print where a figure would go, for a company
# whose unicorn status is sourced but whose valuation no allowlisted source has ever
# published. Two words, because one is not enough and a sentence is too many:
#
#   "Undisclosed"  says the true thing — nobody published a number — in the slot a
#                  reader reads as "how much". On its own it would strip out the only
#                  quantitative fact the register does know.
#   ">1bn"         puts that fact back. No currency symbol, deliberately: the inclusion
#                  rule is "$1B **or** €1B, as reported", and for these records the
#                  source says "reached unicorn status" or "knackte die
#                  Milliarden-Bewertung" without committing to one. Printing "$" here
#                  would be the register asserting a currency nobody used.
#
# Rejected: a bare "—", which is what every other unknown field renders as and would
# read as "worth nothing" beside "$8 bn"; and "€0", which it must never look like.
UNDISCLOSED_VALUATION_LABEL = "Undisclosed"
UNDISCLOSED_VALUATION_BADGE = ">1bn"


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


def _investors_leads_first(record):
    """The detail window's content order mandates leads first among investors,
    but data/companies/*.json just lists `investors` as a flat array — nothing
    in the source data enforces or even implies an order. Settle it here, the
    one place that already owns every other derived label, rather than
    trusting the browser (or the next data file) to get it right.

    A name counts as a lead if it appears in any round's leadInvestors,
    regardless of that round's position in the company's history. Relative
    order is preserved within each group, so this only ever moves leads
    forward — it never reorders leads amongst themselves or non-leads
    amongst themselves.
    """
    investors = record.get("investors") or []
    leads = {name for round_ in record.get("rounds", []) for name in (round_.get("leadInvestors") or [])}
    return [name for name in investors if name in leads] + [name for name in investors if name not in leads]


def _unicorn_labels(record):
    """(threshold, flag) for the crossing: ("$1bn", "crossed $1bn"), or the pair used
    when the crossing round published no price of its own.

    The inclusion rule is "$1B **or** €1B, as reported", and which one a company
    cleared is not decoration. Enpal's crossing round was priced at "€950 million
    ($1.1 billion) post-money": over the dollar threshold, under the euro one. A
    flag hard-coded to "crossed €1bn" sat on that row asserting the opposite of the
    source quoted two inches below it, and the same was true of every record whose
    crossing was reported in dollars. The label follows the crossing round's own
    post-money currency instead, so it can only ever say what the source said.

    A round that carries `undisclosed` instead of a post-money has no currency to
    follow, and falling back to the round's own — the currency of the *money raised* —
    would print "crossed €1bn" off a €160m Series C whose valuation nobody stated. So
    that case says what the source actually says and no more: "reached unicorn status",
    and "Years to unicorn" rather than "Years to €1bn".
    """
    by_id = {entry.get("id"): entry for entry in record.get("rounds", [])}
    unicorn_round = by_id.get(record["becameUnicorn"].get("roundId")) or {}
    if unicorn_round.get("postMoney") is None and unicorn_round.get("undisclosed"):
        return "unicorn", "reached unicorn status"
    currency = (unicorn_round.get("postMoneyCurrency")
                or unicorn_round.get("currency") or "EUR")
    threshold = f"{CURRENCY_SYMBOL.get(currency, currency + ' ')}1bn"
    return threshold, f"crossed {threshold}"


def derive_company(record, today, fx_rate=0.92):
    """today is an as-of reference (year, month) — usually derived from the data's
    own dataAsOf, not the current date. See build()."""
    valuation, rounds = record["valuation"], record["rounds"]
    last_round = rounds[-1] if rounds else None
    unicorn_year, _ = parse_date(record["becameUnicorn"]["date"])
    founders = record.get("founders") or []
    # validate.py guarantees exactly one of the two: an amount, or `undisclosed`
    # evidence that the company is over the threshold. Nothing here has to cope with
    # a record carrying neither.
    valuation_undisclosed = valuation.get("amount") is None
    threshold_label, unicorn_flag_label = _unicorn_labels(record)

    valuation_month = parse_date(valuation["asOf"])
    months_old = _months_between(today, valuation_month)
    months_behind_last_round = (
        _months_between(parse_date(last_round["date"]), valuation_month)
        if last_round else 0)
    aged = (months_old > AGED_AFTER_MONTHS
            or months_behind_last_round > AGED_BEHIND_ROUND_MONTHS)

    display = {
        "valuationLabel": UNDISCLOSED_VALUATION_LABEL if valuation_undisclosed
        else format_amount(
            valuation["amount"], valuation["currency"], valuation.get("approximate", False)),
        "valuationUndisclosed": valuation_undisclosed,
        "valuationUndisclosedBadge": UNDISCLOSED_VALUATION_BADGE if valuation_undisclosed else None,
        # For an undisclosed valuation this is the date the *evidence* was reported —
        # the day an allowlisted page said the company was a unicorn — not the day a
        # figure was struck, because there is no figure. Same field, same staleness
        # rule: evidence ages exactly like a number does.
        "valuationAsOf": format_date(valuation["asOf"]),
        "lastRoundLabel": format_date(last_round["date"]) if last_round else "—",
        "lastRoundStage": last_round["stage"] if last_round else "—",
        # No totalRaisedLabel. `totalRaised` is still carried in the data and still
        # gated by validate.py's quote check — it is sourced, and it may come back —
        # but nothing on the site renders it, so nothing derives a label for it.
        "yearsToUnicorn": unicorn_year - record["foundedYear"],
        "becameUnicornLabel": format_date(record["becameUnicorn"]["date"]),
        "unicornThresholdLabel": threshold_label,
        "unicornFlagLabel": unicorn_flag_label,
        "foundersLabel": ", ".join(f["name"] for f in founders) if founders else "—",
        "aged": aged,
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
        #
        # null for an undisclosed valuation, rather than 0 or a stand-in 1000: there is
        # no figure to order by, and inventing one to make the comparator simpler is
        # inventing one. controls.js sorts those to the end of the highest-valuation
        # list, which is the honest place for "at least a billion, amount unknown".
        "valuationEur": None if valuation_undisclosed
        else _to_eur(valuation["amount"], valuation["currency"], fx_rate),
        "latestRound": list(date_sort_key(last_round["date"])) if last_round else [0, 0],
        "name": record["name"].lower(),
    }
    # `disputed` (a conflicting figure recorded alongside the one on file) needs
    # no derivation of its own — validate.py has already checked its shape and
    # that its source resolves. `**record` below carries the untouched
    # `valuation` object straight into the output, and `**entry` above does the
    # same for a round's, so detail.js reads both from there and renders them
    # with one function. The same is true of the optional top-level
    # `alsoBasedIn` (dual-HQ companies) — it needs no derivation either, just
    # the pass-through.
    return {
        **record,
        "rounds": derived_rounds,
        "display": display,
        "sort": sort,
        "investorsOrdered": _investors_leads_first(record),
    }


def compute_stats(records, fx):
    rate = fx["USD_EUR"]
    # Companies whose valuation is undisclosed are *excluded* from the sum, not counted
    # as zero. Counting them as zero would understate the total by at least a billion
    # each while the headline still claimed to cover the whole register — a wrong figure
    # dressed as a complete one. The label below then says how many of the register the
    # figure actually spans, so a reader can tell the difference without opening a file.
    priced = [r for r in records if r["valuation"].get("amount") is not None]
    combined = sum(
        _to_eur(r["valuation"]["amount"], r["valuation"]["currency"], rate) for r in priced)

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
    # format_amount is exact by design: a company's own figure is rendered to
    # whatever precision the source stated, so a $3.25bn valuation prints as
    # "$3.25 bn" rather than being rounded into a number nobody reported.
    #
    # The combined headline is the one figure here that is not anyone's
    # reported number. It sums mixed currencies through a single disclosed FX
    # rate, which is why it already carries the "~" marker — and exactness
    # would actively mislead: the current total lands on 75002, which rendered
    # verbatim reads "~€75.002 bn" and implies a precision to the nearest
    # million that an FX-converted aggregate cannot support. So this derived
    # figure, and only this one, is rounded to a tenth of a billion before it
    # is labelled. The unrounded sum stays in combinedValuationEurMillions for
    # anyone who wants to recompute it.
    #
    # ROUND_HALF_UP, not Python's built-in round(): the builtin rounds half to
    # even, so a combined of 75050 would label "~€75 bn" rather than
    # "~€75.1 bn" — the same banker's-rounding trap that made format_amount
    # print a $3.25bn valuation as "$3.2 bn". _billion_forms already rounds
    # this way; rounding half-up in one place and half-to-even in another is
    # how that defect got in.
    combined_label_value = int(
        (Decimal(str(combined)) / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)) * 100
    return {
        "count": len(records),
        "combinedValuationEurMillions": combined,
        "combinedValuationLabel": format_amount(combined_label_value, "EUR", True),
        "combinedValuationCount": len(priced),
        # The stat's own caption, settled here rather than hard-coded in register.js,
        # because it is a fact about the data: "Combined value" is only the whole truth
        # when every record contributed one.
        "combinedValuationBasis": "Combined value" if len(priced) == len(records)
        else f"Combined value · {len(priced)} of {len(records)} disclosed",
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


# ---------------------------------------------------------------------------
# The weekly funding round-up.
#
# A deliberately separate payload from data/companies.json. The register's
# promise is that every figure is quote-checked; the round-up's is that every
# round is sourced and linked. Merging them into one file would invite a reader
# — and, worse, a future renderer — to treat one standard as the other's. The
# page says which is which in a single line above the block; the data keeps
# them in separate files so nothing has to remember.
# ---------------------------------------------------------------------------

# Rendered where a founder list would go when the source never printed one.
# Not "—": the sentence reads "Company X, from founders Y, secured Z", and an
# em dash in the middle of it asserts that the founders are unknown to anyone.
# What is actually true is that this source did not name them, so the clause is
# dropped entirely and the sentence closes up around the gap.
NO_FOUNDERS_LABEL = None


def _day_label(date_str, with_year=True, with_month=True):
    """"23 Jul 2026" from a YYYY-MM-DD string, with either tail trimmable so a
    date range can share its month and year rather than repeating them."""
    year, month, day = int(date_str[0:4]), int(date_str[5:7]), int(date_str[8:10])
    parts = [str(day)]
    if with_month:
        parts.append(MONTHS[month - 1])
    if with_year:
        parts.append(str(year))
    return " ".join(parts)


def format_range(start, end):
    """"20–26 Jul 2026", or "27 Jul – 2 Aug 2026" across a month boundary.

    An en dash, and spaced only when the operands themselves contain spaces —
    "20–26 Jul" reads as one span, "27 Jul–2 Aug" reads as a typo.
    """
    same_year = start[0:4] == end[0:4]
    same_month = same_year and start[5:7] == end[5:7]
    if same_month:
        return f"{_day_label(start, with_year=False, with_month=False)}–{_day_label(end)}"
    if same_year:
        return f"{_day_label(start, with_year=False)} – {_day_label(end)}"
    return f"{_day_label(start)} – {_day_label(end)}"


def format_names(names):
    """"A, B and C" — the serial comma deliberately omitted, because this runs
    inside the owner's sentence template rather than standing on its own."""
    names = [n for n in (names or []) if n]
    if not names:
        return NO_FOUNDERS_LABEL
    if len(names) == 1:
        return names[0]
    return f"{', '.join(names[:-1])} and {names[-1]}"


def derive_round(entry):
    """Every label the browser prints, settled here.

    `valuationLabel` is None rather than "—" when no valuation was reported:
    the owner's format puts it in parentheses, and "(at a — valuation)" is
    worse than no parenthetical at all. The renderer omits the clause.
    """
    amount_label = format_amount(
        entry["amount"], entry["currency"], entry.get("approximate", False))
    valuation = entry.get("valuation")
    valuation_label = (
        format_amount(valuation, entry.get("valuationCurrency") or entry["currency"], False)
        if valuation is not None else None)
    source = entry["source"]
    derived = {
        **entry,
        "amountLabel": amount_label,
        "valuationLabel": valuation_label,
        "foundersLabel": format_names(entry.get("founders")),
        "investorsLabel": format_names(entry.get("investors")),
        "source": {**source, "publishedLabel": _day_label(source["publishedOn"])},
    }
    # A conflicting figure recorded beside the published one, with its own
    # citation — the round-up's counterpart to the register's `disputed`, and
    # dated the same way so the two figures are equally traceable.
    note = entry.get("note")
    if note:
        derived["note"] = {
            **note,
            "source": {**note["source"],
                       "publishedLabel": _day_label(note["source"]["publishedOn"])},
        }
    return derived


def derive_week(record):
    lead = [derive_round(entry) for entry in record["lead"]]
    more = [derive_round(entry) for entry in record["more"]]
    return {
        **record,
        "lead": lead,
        "more": more,
        "rangeLabel": format_range(record["start"], record["end"]),
        # "W30" is what the selectable card shows; the week id carries the year
        # for anything that needs to disambiguate across a new year.
        "shortLabel": f"W{record['week'].split('-W')[1]}",
        "yearLabel": record["week"].split("-W")[0],
        "roundCount": len(lead) + len(more),
        "moreCount": len(more),
    }


def build_funding(src="data/funding", out="data/funding.json"):
    """Merge the weekly files into one payload, newest first.

    Newest-first is a string sort on the ISO week id, which is correct because
    the id is zero-padded and year-major ("2026-W09" < "2026-W30" < "2027-W01").
    No wall clock is consulted: which week is newest is a fact about the files.
    """
    records = [
        json.loads(f.read_text(encoding="utf-8"))
        for f in sorted(pathlib.Path(src).glob("*.json"))
    ]
    weeks = [derive_week(record) for record in
             sorted(records, key=lambda r: r["week"], reverse=True)]
    payload = {
        "weeks": weeks,
        "stats": {
            "weekCount": len(weeks),
            "roundCount": sum(week["roundCount"] for week in weeks),
            # The newest week is what the block selects by default. Settled here
            # so the browser never has to decide "newest" for itself.
            "latestWeek": weeks[0]["week"] if weeks else None,
        },
    }
    out_path = pathlib.Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = build()
    print(f"Built {result['stats']['count']} companies -> data/companies.json")
    funding = build_funding()
    print(f"Built {funding['stats']['weekCount']} funding weeks "
          f"({funding['stats']['roundCount']} rounds) -> data/funding.json")
