# tests/test_build.py
import json, pathlib, pytest
from tools.build import build, derive_company, compute_stats

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "valid_company.json"
FX = {"USD_EUR": 0.92, "asOf": "2026-08"}


@pytest.fixture
def record():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_display_labels_are_precomputed_for_the_grid(record):
    display = derive_company(record, today=(2026, 8))["display"]
    assert display["valuationLabel"] == "~€1.2 bn"
    assert display["lastRoundLabel"] == "Mar 2024"


def test_total_raised_is_kept_in_the_data_but_no_longer_labelled(record):
    """The field is still sourced and still quote-checked by validate.py — it just
    stopped being rendered, so nothing derives a display label for it."""
    derived = derive_company(record, today=(2026, 8))
    assert "totalRaisedLabel" not in derived["display"]
    assert derived["totalRaised"]["amount"] == 300


def test_years_to_unicorn_is_derived_from_founding_year(record):
    assert derive_company(record, today=(2026, 8))["display"]["yearsToUnicorn"] == 9


def test_a_valuation_the_company_has_since_raised_past_is_flagged_aged(record):
    """The marker's primary meaning: money came in after the last published price
    and nobody restated it. The fixture's valuation and its last round share a
    month, so it takes a later round to trip this."""
    record["rounds"].append({
        "id": "r3", "date": "2026-06", "stage": "Series D", "amount": 120,
        "currency": "EUR", "approximate": False, "postMoney": None,
        "leadInvestors": ["Index Ventures"], "investors": ["Index Ventures"],
        "source": "s1"})
    assert derive_company(record, today=(2026, 8))["display"]["aged"] is True


def test_a_round_close_behind_the_valuation_is_not_flagged_aged(record):
    """Raising within two years of the last published price is ordinary, not stale."""
    record["rounds"].append({
        "id": "r3", "date": "2025-06", "stage": "Series D", "amount": 120,
        "currency": "EUR", "approximate": False, "postMoney": None,
        "leadInvestors": ["Index Ventures"], "investors": ["Index Ventures"],
        "source": "s1"})
    assert derive_company(record, today=(2026, 8))["display"]["aged"] is False


def test_a_quiet_company_is_flagged_aged_only_after_five_years(record):
    """The backstop. Four years was tested against the real register and still
    flagged a third of it, so the badge would have gone on meaning nothing."""
    assert derive_company(record, today=(2028, 3))["display"]["aged"] is False
    assert derive_company(record, today=(2029, 4))["display"]["aged"] is True


def test_sort_keys_normalise_currency_for_ordering_only(record):
    record["valuation"] = {**record["valuation"], "amount": 1000, "currency": "USD"}
    derived = derive_company(record, today=(2026, 8))
    assert derived["sort"]["valuationEur"] == pytest.approx(920)
    assert derived["display"]["valuationLabel"] == "~$1 bn"


def test_missing_optional_data_becomes_a_dash(record):
    """An en dash, not an em dash: em dashes are banned from every visible string
    on the site (docs/BRAND.md), and this one is as visible as copy gets."""
    record["founders"] = []
    assert derive_company(record, today=(2026, 8))["display"]["foundersLabel"] == "–"


def test_round_labels_are_precomputed(record):
    from tools.build import derive_company
    rounds = derive_company(record, today=(2026, 8))["rounds"]
    assert rounds[1]["dateLabel"] == "Mar 2024"
    assert rounds[1]["amountLabel"] == "€120 m"


def test_investors_are_ordered_leads_first(record):
    # "Cherry Ventures" never leads a round; "Index Ventures" and "Earlybird"
    # each lead one (r2 and r1 respectively). Listing the non-lead first in
    # the source data must not survive into the derived order.
    record["investors"] = ["Cherry Ventures", "Index Ventures", "Earlybird"]
    investors_ordered = derive_company(record, today=(2026, 8))["investorsOrdered"]
    assert investors_ordered == ["Index Ventures", "Earlybird", "Cherry Ventures"]


def test_stats_combine_valuations_at_the_disclosed_rate(record):
    other = json.loads(FIXTURE.read_text(encoding="utf-8"))
    other["slug"] = "second-gmbh"
    other["valuation"] = {**other["valuation"], "amount": 1000, "currency": "USD"}
    stats = compute_stats(
        [derive_company(record, (2026, 8)), derive_company(other, (2026, 8))], FX)
    assert stats["count"] == 2
    assert stats["combinedValuationEurMillions"] == pytest.approx(2120)
    assert stats["fxRateDisclosed"] == 0.92


def test_the_combined_headline_is_rounded_but_the_underlying_sum_is_not(record):
    """The one derived figure that must not inherit format_amount's exactness.

    format_amount now renders a company's own valuation to whatever precision
    the source stated, which is right for a sourced figure. The combined total
    is nobody's reported number — it sums mixed currencies through one
    disclosed FX rate — so rendering it verbatim would print something like
    "~€75.002 bn" and imply accuracy to the nearest million. The label is
    rounded to a tenth of a billion; the exact sum stays in the payload.
    """
    other = json.loads(FIXTURE.read_text(encoding="utf-8"))
    other["slug"] = "second-gmbh"
    other["valuation"] = {**other["valuation"], "amount": 73_002, "currency": "EUR"}
    stats = compute_stats(
        [derive_company(record, (2026, 8)), derive_company(other, (2026, 8))], FX)
    assert stats["combinedValuationEurMillions"] == pytest.approx(74_202)
    assert stats["combinedValuationLabel"] == "~€74.2 bn"


def test_the_combined_headline_rounds_a_half_up_not_to_even(record):
    """round() would send 75050 to "~€75 bn"; half-up sends it to "~€75.1 bn".

    Python's builtin rounds half to even, which is the trap that made
    format_amount print $3.25bn as "$3.2 bn". Rounding half-up here and
    half-to-even there is how that defect got in, so both use Decimal.
    """
    other = json.loads(FIXTURE.read_text(encoding="utf-8"))
    other["slug"] = "second-gmbh"
    other["valuation"] = {**other["valuation"], "amount": 73_850, "currency": "EUR"}
    stats = compute_stats(
        [derive_company(record, (2026, 8)), derive_company(other, (2026, 8))], FX)
    assert stats["combinedValuationEurMillions"] == pytest.approx(75_050)
    assert stats["combinedValuationLabel"] == "~€75.1 bn"


def test_stats_count_new_unicorns_in_the_last_twelve_months():
    base = json.loads(FIXTURE.read_text(encoding="utf-8"))
    recent = derive_company({**base, "becameUnicorn": {**base["becameUnicorn"], "date": "2026-02"}}, (2026, 8))
    old = derive_company({**base, "slug": "old-gmbh"}, (2026, 8))
    stats = compute_stats([recent, old], FX)
    assert stats["newInLast12Months"] == 1


def test_the_build_output_is_a_pure_function_of_its_inputs(tmp_path):
    """companies.json is committed and CI diffs it — the clock must not leak in."""
    src = tmp_path / "companies"
    src.mkdir()
    (src / "example-gmbh.json").write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    fx = tmp_path / "fx.json"
    fx.write_text(json.dumps({"USD_EUR": 0.92, "asOf": "2026-08"}), encoding="utf-8")

    first = build(src=str(src), out=str(tmp_path / "a.json"), fx_path=str(fx))
    second = build(src=str(src), out=str(tmp_path / "b.json"), fx_path=str(fx))

    assert first == second
    assert (tmp_path / "a.json").read_text() == (tmp_path / "b.json").read_text()
    assert "generatedOn" not in first["stats"]
    assert first["stats"]["dataAsOf"] == "2024-03-14"
    assert first["companies"][0]["display"]["aged"] is False, (
        "aged must be measured from dataAsOf, not the wall clock")


def test_a_missing_publishedon_raises_instead_of_building_on_nonsense(tmp_path):
    base = json.loads(FIXTURE.read_text(encoding="utf-8"))
    base["sources"] = [{**s, "publishedOn": ""} for s in base["sources"]]
    src = tmp_path / "companies"
    src.mkdir()
    (src / "example-gmbh.json").write_text(json.dumps(base), encoding="utf-8")
    fx = tmp_path / "fx.json"
    fx.write_text(json.dumps({"USD_EUR": 0.92, "asOf": "2026-08"}), encoding="utf-8")

    with pytest.raises(ValueError, match="publishedOn"):
        build(src=str(src), out=str(tmp_path / "out.json"), fx_path=str(fx))


def test_unicorn_threshold_label_follows_the_crossing_round_currency(record):
    """The inclusion rule is "$1B or €1B, as reported", so the flag on the crossing
    round must name the threshold that round actually cleared. Enpal's crossing was
    "€950 million ($1.1 billion) post-money" — over $1bn, under €1bn — and a
    hard-coded "crossed €1bn" asserted the opposite of the quote beside it."""
    record["rounds"][1]["postMoney"] = 1100
    record["rounds"][1]["postMoneyCurrency"] = "USD"
    derived = derive_company(record, (2024, 3))
    assert derived["display"]["unicornThresholdLabel"] == "$1bn"


def test_unicorn_threshold_label_defaults_to_the_round_currency(record):
    assert derive_company(record, (2024, 3))["display"]["unicornThresholdLabel"] == "€1bn"


def test_the_crossing_flag_names_the_threshold_when_the_round_was_priced(record):
    assert derive_company(record, (2024, 3))["display"]["unicornFlagLabel"] == "crossed €1bn"


# --------------------------------------------------------------------------------------
# Undisclosed valuations, rendered.
# --------------------------------------------------------------------------------------

def _undisclosed(record):
    record["sources"].append({
        "id": "s3", "publication": "TechCrunch", "title": "Europe's new unicorns",
        "url": "https://techcrunch.com/2025/09/08/new-unicorns/", "publishedOn": "2025-09-08",
        "quote": "German startup Example GmbH became a unicorn in March."})
    record["valuation"] = {
        "amount": None, "currency": None, "approximate": False, "asOf": "2025-09",
        "round": "Series C", "source": "s1",
        "undisclosed": {"note": "No allowlisted source states a figure.", "source": "s3"}}
    record["rounds"][1]["postMoney"] = None
    record["rounds"][1]["undisclosed"] = {"note": "Price never published.", "source": "s3"}
    return record


def test_an_undisclosed_valuation_never_renders_as_a_figure_or_a_dash(record):
    """It must not read as "worth nothing" beside real numbers, and it must not read as
    a number nobody published either."""
    display = derive_company(_undisclosed(record), today=(2026, 8))["display"]
    assert display["valuationLabel"] == "Undisclosed"
    assert display["valuationUndisclosed"] is True
    assert display["valuationUndisclosedBadge"] == ">1bn"


def test_a_priced_valuation_carries_no_undisclosed_marker(record):
    display = derive_company(record, today=(2026, 8))["display"]
    assert display["valuationUndisclosed"] is False
    assert display["valuationUndisclosedBadge"] is None


def test_a_qualitative_crossing_says_so_rather_than_naming_a_threshold(record):
    """Falling back to the round's own currency would print "crossed €1bn" off the
    currency of the money *raised*, which is a different number in a different sentence."""
    display = derive_company(_undisclosed(record), today=(2026, 8))["display"]
    assert display["unicornFlagLabel"] == "reached unicorn status"
    assert display["unicornThresholdLabel"] == "unicorn"


def test_an_undisclosed_valuation_has_no_sort_key_rather_than_a_zero(record):
    derived = derive_company(_undisclosed(record), today=(2026, 8))
    assert derived["sort"]["valuationEur"] is None


def test_an_undisclosed_valuation_still_ages(record):
    """asOf on an undisclosed valuation dates the evidence, and evidence goes stale
    exactly like a figure does."""
    undisclosed = _undisclosed(record)
    assert derive_company(undisclosed, today=(2030, 10))["display"]["aged"] is True
    assert derive_company(undisclosed, today=(2026, 8))["display"]["aged"] is False


def test_the_combined_stat_excludes_undisclosed_records_rather_than_counting_them_as_zero(record):
    other = json.loads(FIXTURE.read_text(encoding="utf-8"))
    other["slug"] = "second-gmbh"
    stats = compute_stats(
        [derive_company(record, (2026, 8)),
         derive_company(_undisclosed(other), (2026, 8))], FX)
    assert stats["count"] == 2
    assert stats["combinedValuationEurMillions"] == pytest.approx(1200)
    assert stats["combinedValuationCount"] == 1


def test_the_combined_stat_caption_says_what_it_actually_sums(record):
    """A total covering part of the register must not be captioned as covering all of
    it — the reader has to be able to tell without opening a data file."""
    other = json.loads(FIXTURE.read_text(encoding="utf-8"))
    other["slug"] = "second-gmbh"
    partial = compute_stats(
        [derive_company(record, (2026, 8)),
         derive_company(_undisclosed(other), (2026, 8))], FX)
    assert partial["combinedValuationBasis"] == "Combined value · 1 of 2 disclosed"

    whole = compute_stats([derive_company(record, (2026, 8))], FX)
    assert whole["combinedValuationBasis"] == "Combined value"


# --- the two shapes the Companies intro draws --------------------------------
# Both are derived here rather than in the browser so the picture cannot drift
# from the register. These tests pin the properties the drawings depend on: a
# contiguous span of years, and a partition that sums to the register's size.


def _crossing_in(record, date, slug):
    return derive_company(
        {**record, "slug": slug, "becameUnicorn": {**record["becameUnicorn"], "date": date}},
        (2026, 8))


def test_crossings_by_year_spans_every_year_including_the_quiet_ones(record):
    stats = compute_stats([
        _crossing_in(record, "2021-03", "a-gmbh"),
        _crossing_in(record, "2021-09", "b-gmbh"),
        _crossing_in(record, "2023-05", "c-gmbh"),
    ], FX)
    assert stats["crossingsByYear"] == [
        {"year": 2021, "count": 2},
        {"year": 2022, "count": 0},
        {"year": 2023, "count": 1},
    ]


def test_crossings_by_year_totals_the_register(record):
    """The strip is the register seen along a time axis, so nothing may fall out of it."""
    stats = compute_stats([
        _crossing_in(record, "2019-01", "a-gmbh"),
        _crossing_in(record, "2026-07", "b-gmbh"),
        _crossing_in(record, "2026-08", "c-gmbh"),
    ], FX)
    assert sum(entry["count"] for entry in stats["crossingsByYear"]) == stats["count"] == 3


def test_an_empty_register_yields_no_strip_and_no_bar_rather_than_an_empty_axis():
    stats = compute_stats([], FX)
    assert stats["crossingsByYear"] == []
    assert stats["sectorComposition"] == []


def test_sector_composition_is_a_partition_ordered_largest_first(record):
    def in_sectors(slug, sectors):
        return derive_company({**record, "slug": slug, "sectors": sectors}, (2026, 8))

    stats = compute_stats([
        in_sectors("a-gmbh", ["Fintech"]),
        in_sectors("b-gmbh", ["Fintech"]),
        in_sectors("c-gmbh", ["Climate and Energy"]),
    ], FX)
    assert stats["sectorComposition"] == [
        {"sector": "Fintech", "count": 2},
        {"sector": "Climate and Energy", "count": 1},
    ]
    assert sum(entry["count"] for entry in stats["sectorComposition"]) == stats["count"]


def test_a_company_in_several_sectors_is_placed_once_under_the_first(record):
    """The chips match on every sector a company lists, but a composition bar has to
    place each company exactly once or its widths stop summing to anything."""
    multi = derive_company(
        {**record, "slug": "multi-gmbh", "sectors": ["Fintech", "Artificial Intelligence"]},
        (2026, 8))
    stats = compute_stats([multi], FX)
    assert stats["sectorComposition"] == [{"sector": "Fintech", "count": 1}]
    assert sum(entry["count"] for entry in stats["sectorComposition"]) == stats["count"] == 1


def test_sector_ties_break_on_name_so_the_bar_cannot_reshuffle_between_builds(record):
    def in_sectors(slug, sector):
        return derive_company({**record, "slug": slug, "sectors": [sector]}, (2026, 8))

    ordered = compute_stats([in_sectors("a", "Zeta"), in_sectors("b", "Alpha")], FX)
    reversed_ = compute_stats([in_sectors("b", "Alpha"), in_sectors("a", "Zeta")], FX)
    assert ordered["sectorComposition"] == reversed_["sectorComposition"]
    assert [entry["sector"] for entry in ordered["sectorComposition"]] == ["Alpha", "Zeta"]
