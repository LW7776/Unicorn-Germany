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
    assert display["totalRaisedLabel"] == "~€300 m"


def test_years_to_unicorn_is_derived_from_founding_year(record):
    assert derive_company(record, today=(2026, 8))["display"]["yearsToUnicorn"] == 9


def test_a_valuation_older_than_24_months_is_flagged_aged(record):
    assert derive_company(record, today=(2026, 8))["display"]["aged"] is True
    assert derive_company(record, today=(2025, 3))["display"]["aged"] is False


def test_sort_keys_normalise_currency_for_ordering_only(record):
    record["valuation"] = {**record["valuation"], "amount": 1000, "currency": "USD"}
    derived = derive_company(record, today=(2026, 8))
    assert derived["sort"]["valuationEur"] == pytest.approx(920)
    assert derived["display"]["valuationLabel"] == "~$1 bn"


def test_missing_optional_data_becomes_an_em_dash(record):
    record["founders"] = []
    assert derive_company(record, today=(2026, 8))["display"]["foundersLabel"] == "—"


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
