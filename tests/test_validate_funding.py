# tests/test_validate_funding.py
import copy
import json
import pathlib

import pytest

from tools.validate_funding import (
    MAX_MORE, is_resolvable_url, validate_directory, validate_week, week_bounds)

WEEKS = pathlib.Path(__file__).parent.parent / "data" / "funding"


def a_round(**overrides):
    entry = {
        "id": "m1",
        "company": "Example GmbH",
        "hq": "Berlin",
        "stage": "Series A",
        "amount": 12.5,
        "currency": "EUR",
        "approximate": False,
        "valuation": None,
        "valuationCurrency": None,
        "founders": ["Ada Beispiel"],
        "investors": ["Some Fund"],
        "source": {
            "publication": "Tech.eu",
            "title": "Example GmbH raises €12.5M",
            "url": "https://tech.eu/2026/07/22/example/",
            "publishedOn": "2026-07-22",
        },
    }
    entry.update(overrides)
    return entry


@pytest.fixture
def week():
    return {
        "week": "2026-W30",
        "start": "2026-07-20",
        "end": "2026-07-26",
        "lead": [dict(a_round(id="l1"), text="A paragraph of real prose.")],
        "more": [a_round()],
    }


# --- the shipped data -------------------------------------------------------

def test_every_published_week_validates():
    assert validate_directory(str(WEEKS)) == {}


def test_every_published_round_carries_a_link_and_a_date():
    for file in sorted(WEEKS.glob("*.json")):
        record = json.loads(file.read_text(encoding="utf-8"))
        for entry in record["lead"] + record["more"]:
            source = entry["source"]
            assert is_resolvable_url(source["url"]), (file.stem, entry["id"])
            assert len(source["publishedOn"]) == 10, (file.stem, entry["id"])


# --- week identity ----------------------------------------------------------

def test_week_bounds_are_the_iso_monday_and_sunday():
    assert week_bounds("2026-W30") == ("2026-07-20", "2026-07-26")
    assert week_bounds("2026-W32") == ("2026-08-03", "2026-08-09")


def test_a_week_that_does_not_exist_is_rejected():
    # 2026 is a 53-week ISO year and 2025 is not, so W53 is real in one and a
    # typo in the other. The check has to know the difference rather than
    # capping every year at 52.
    assert week_bounds("2026-W53") == ("2026-12-28", "2027-01-03")
    with pytest.raises(ValueError):
        week_bounds("2025-W53")
    with pytest.raises(ValueError):
        week_bounds("2026-W54")
    with pytest.raises(ValueError):
        week_bounds("2026-30")


def test_a_range_that_disagrees_with_the_week_id_is_an_error(week):
    week["end"] = "2026-07-27"
    assert any("must be the Sunday" in e for e in validate_week(week))


# --- the two caps -----------------------------------------------------------

def test_more_than_five_additional_rounds_is_a_clear_error(week):
    week["more"] = [a_round(id=f"m{i}") for i in range(MAX_MORE + 1)]
    errors = validate_week(week)
    assert any(f"the cap is {MAX_MORE}" in e for e in errors)


def test_exactly_five_additional_rounds_is_fine(week):
    week["more"] = [a_round(id=f"m{i}") for i in range(MAX_MORE)]
    assert validate_week(week) == []


def test_a_third_lead_round_is_rejected(week):
    week["lead"] = [dict(a_round(id=f"l{i}"), text="Prose.") for i in range(3)]
    assert any("at most 2" in e for e in validate_week(week))


def test_a_week_with_no_lead_round_is_rejected(week):
    week["lead"] = []
    assert any("at least one" in e for e in validate_week(week))


# --- the lead / more distinction --------------------------------------------

def test_a_lead_round_without_prose_is_rejected(week):
    week["lead"][0]["text"] = "   "
    assert any("move it to `more`" in e for e in validate_week(week))


def test_an_additional_round_carrying_prose_is_rejected(week):
    week["more"][0]["text"] = "This belongs in a lead."
    assert any("listed, not written up" in e for e in validate_week(week))


# --- sourcing (linked and dated, never quote-gated) -------------------------

def test_an_unlinkable_source_url_is_rejected(week):
    for bad in ("javascript:alert(1)", "not a url", "/relative/path", ""):
        record = copy.deepcopy(week)
        record["more"][0]["source"]["url"] = bad
        assert any("absolute http(s) URL" in e for e in validate_week(record)), bad


def test_a_publication_off_the_allowlist_is_rejected(week):
    week["more"][0]["source"]["publication"] = "Some Blog"
    assert any("not on the allowlist" in e for e in validate_week(week))


def test_a_partial_publication_date_is_rejected(week):
    week["more"][0]["source"]["publishedOn"] = "2026-07"
    assert any("YYYY-MM-DD" in e for e in validate_week(week))


def test_coverage_published_after_the_week_is_allowed(week):
    """A Friday round routinely lands in the following Monday's weekly recap."""
    week["more"][0]["source"]["publishedOn"] = "2026-08-03"
    assert validate_week(week) == []


def test_coverage_published_before_the_week_is_rejected(week):
    week["more"][0]["source"]["publishedOn"] = "2026-07-19"
    assert any("predates the week" in e for e in validate_week(week))


def test_no_quote_is_required_anywhere(week):
    """The round-up's standard is lighter than the register's by design: a round
    with no quote field at all validates. Adding one is an unknown field."""
    assert validate_week(week) == []
    week["more"][0]["quote"] = "…"
    assert any("unknown field 'quote'" in e for e in validate_week(week))


# --- figures ----------------------------------------------------------------

def test_an_unknown_currency_is_rejected(week):
    week["more"][0]["currency"] = "GBP"
    assert any("not a currency this site can render" in e for e in validate_week(week))


def test_a_missing_or_zero_amount_is_rejected(week):
    week["more"][0]["amount"] = None
    assert any("must be a number of millions" in e for e in validate_week(week))
    week["more"][0]["amount"] = 0
    assert any("greater than zero" in e for e in validate_week(week))


def test_a_valuation_needs_its_own_currency(week):
    week["more"][0]["valuation"] = 1000
    assert any("valuationCurrency is required" in e for e in validate_week(week))
    week["more"][0]["valuationCurrency"] = "EUR"
    assert validate_week(week) == []


def test_a_currency_with_no_valuation_under_it_is_rejected(week):
    week["more"][0]["valuationCurrency"] = "EUR"
    assert any("label for nothing" in e for e in validate_week(week))


# --- shape discipline -------------------------------------------------------

# --- a conflicting figure, recorded rather than reconciled ------------------

A_NOTE = {
    "text": "€35m is the company's own figure; the trade press reports €30m.",
    "source": {
        "publication": "Sifted",
        "title": "Company raises €30m",
        "url": "https://sifted.eu/articles/x/",
        "publishedOn": "2026-07-23",
    },
}


def test_a_note_carrying_the_other_figure_is_valid(week):
    week["more"][0]["note"] = A_NOTE
    assert validate_week(week) == []


def test_a_note_must_carry_its_own_source(week):
    """The point of the note is that the *other* figure is as traceable as the
    published one — a bare sentence would make it less so, not more."""
    week["more"][0]["note"] = {"text": "The trade press reports €30m."}
    assert any("note is missing source" in e for e in validate_week(week))


def test_a_notes_source_is_held_to_the_same_standard(week):
    week["more"][0]["note"] = {**A_NOTE,
                               "source": {**A_NOTE["source"], "publication": "Some Blog"}}
    assert any("note.source publication not on the allowlist" in e
               for e in validate_week(week))
    week["more"][0]["note"] = {**A_NOTE,
                               "source": {**A_NOTE["source"], "url": "not a url"}}
    assert any("note.source.url must be an absolute" in e for e in validate_week(week))


def test_an_empty_note_is_rejected(week):
    week["more"][0]["note"] = {**A_NOTE, "text": "  "}
    assert any("note.text must be a non-empty string" in e for e in validate_week(week))


def test_the_moss_round_publishes_the_companys_own_figure_and_says_no_more():
    """€35m comes from Moss's own announcement of its own round, and a note
    explaining that three publications printed €30m adds nothing a reader can act
    on. The disputed marker is reserved for a disagreement that would change what
    somebody believes, so this round carries none, on either side of the site."""
    record = json.loads((WEEKS / "2026-W32.json").read_text(encoding="utf-8"))
    moss = next(r for r in record["lead"] if r["company"] == "Moss")
    assert moss["amount"] == 35
    assert moss["source"]["publication"] == "Company press release"
    assert "note" not in moss
    assert "€35m" in moss["text"] and "€30m" not in moss["text"]

    register = json.loads(
        (WEEKS.parent / "companies" / "moss.json").read_text(encoding="utf-8"))
    series_c = next(r for r in register["rounds"] if r["stage"] == "Series C")
    assert "disputed" not in series_c
    assert "disputed" not in register["valuation"]


def test_the_register_and_the_roundup_agree_on_moss():
    """The check that would have caught this: the two datasets must not state
    different figures for the same round."""
    register = json.loads(
        (WEEKS.parent / "companies" / "moss.json").read_text(encoding="utf-8"))
    series_c = next(r for r in register["rounds"] if r["stage"] == "Series C")
    record = json.loads((WEEKS / "2026-W32.json").read_text(encoding="utf-8"))
    moss = next(r for r in record["lead"] if r["company"] == "Moss")
    assert moss["amount"] == series_c["amount"]
    assert moss["currency"] == series_c["currency"]
    assert moss["valuation"] == series_c["postMoney"]


def test_a_misspelled_optional_field_is_rejected_by_name(week):
    week["more"][0]["valuationCurency"] = "EUR"
    assert any("unknown field 'valuationCurency'" in e for e in validate_week(week))


def test_founders_may_be_empty_but_never_invented(week):
    week["more"][0]["founders"] = []
    assert validate_week(week) == []
    week["more"][0]["founders"] = None
    assert any("must be a list" in e for e in validate_week(week))


def test_duplicate_ids_across_lead_and_more_collide(week):
    week["more"][0]["id"] = "l1"
    assert any("duplicate id" in e for e in validate_week(week))
