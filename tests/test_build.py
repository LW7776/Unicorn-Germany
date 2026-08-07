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
