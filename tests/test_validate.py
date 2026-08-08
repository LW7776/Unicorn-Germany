import json, pathlib, pytest
from tools.validate import validate_company

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "valid_company.json"


@pytest.fixture
def record():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_the_reference_record_is_valid(record):
    assert validate_company(record) == []


def test_missing_required_field_is_an_error(record):
    del record["website"]
    assert any("website" in e for e in validate_company(record))


def test_figure_citing_an_unknown_source_is_an_error(record):
    record["valuation"]["source"] = "s99"
    assert any("s99" in e for e in validate_company(record))


def test_source_outside_the_allowlist_is_an_error(record):
    record["sources"][0]["publication"] = "Crunchbase"
    assert any("Crunchbase" in e for e in validate_company(record))


def test_source_without_a_full_publication_date_is_an_error(record):
    record["sources"][0]["publishedOn"] = "2024-03"
    assert any("publishedOn" in e for e in validate_company(record))


def test_quote_that_does_not_contain_the_figure_is_an_error(record):
    record["sources"][0]["quote"] = "Example GmbH announced a funding round today."
    errors = validate_company(record)
    assert any("quote" in e for e in errors)


def test_rounds_out_of_chronological_order_is_an_error(record):
    record["rounds"][0]["date"], record["rounds"][1]["date"] = "2024-03", "2021-05"
    assert any("chronological" in e for e in validate_company(record))


def test_unicorn_round_below_the_threshold_is_an_error(record):
    record["rounds"][1]["postMoney"] = 400
    record["valuation"]["amount"] = 400
    assert any("threshold" in e for e in validate_company(record))


def test_a_dollar_billion_round_meets_the_threshold(record):
    record["rounds"][1]["currency"] = "USD"
    record["rounds"][1]["postMoney"] = 1000
    record["valuation"] = {"amount": 1000, "currency": "USD", "approximate": True,
                           "asOf": "2024-03", "round": "Series C", "source": "s1"}
    record["sources"][0]["quote"] = (
        "Example GmbH raised 120 million euros at a valuation of about 1 billion dollars, "
        "and has raised 300 million euros in total.")
    assert validate_company(record) == []


def test_valuation_predating_a_last_round_that_discloses_a_post_money_is_an_error(record):
    """The case worth catching: a newer round priced the company and the record
    is still showing the older figure. This is the Parloa error."""
    record["valuation"]["asOf"] = "2022-01"
    assert any("predates" in e for e in validate_company(record))


def test_valuation_predating_a_last_round_with_no_post_money_is_valid(record):
    """Ordinary and honest: the company raised and said nothing about valuation.

    Rejecting this shape kept Enpal, Scalable Capital and 1KOMMA5° out of the
    register over evidence that does not exist — each has a sound valuation and
    a later round whose price was simply never announced.
    """
    record["rounds"].append({
        "id": "r3", "date": "2025-06", "stage": "Series D", "amount": None,
        "currency": "EUR", "approximate": False, "postMoney": None,
        "leadInvestors": [], "investors": [], "source": "s1"})
    # valuation.asOf stays 2024-03 — now older than the 2025-06 round, which
    # disclosed no price. This is Razor Group's shape, and Enpal's.
    assert validate_company(record) == []


def test_valuation_at_or_after_the_last_round_is_valid(record):
    """Unchanged behaviour: the reference record dates both to 2024-03."""
    assert validate_company(record) == []
    record["valuation"]["asOf"] = "2025-06"
    assert validate_company(record) == []


def test_a_disclosed_post_money_mid_history_also_supersedes_the_valuation(record):
    """Looking only at rounds[-1] would miss this.

    A priced round in the middle of the history supersedes the headline just as
    surely as one at the end, even when the newest round of all disclosed nothing.
    """
    record["valuation"]["asOf"] = "2022-01"
    record["rounds"].append({
        "id": "r3", "date": "2025-01", "stage": "Series D", "amount": None,
        "currency": "EUR", "approximate": False, "postMoney": None,
        "leadInvestors": [], "investors": [], "source": "s1"})
    errors = validate_company(record)
    assert any("predates round r2" in e for e in errors)


def test_a_round_in_the_same_month_as_the_valuation_is_the_round_that_set_it(record):
    """Strictly-after, not on-or-after: r2 and the valuation share 2024-03."""
    assert validate_company(record) == []


def test_unknown_unicorn_round_id_is_an_error(record):
    record["becameUnicorn"]["roundId"] = "r9"
    assert any("r9" in e for e in validate_company(record))


def test_slug_must_be_url_safe(record):
    record["slug"] = "Example GmbH"
    assert any("slug" in e for e in validate_company(record))


def test_a_figure_hiding_inside_a_longer_number_is_not_sourced(record):
    record["totalRaised"]["amount"] = 20        # "20" appears only inside "120"
    assert any("quote" in e for e in validate_company(record))


def test_unquoted_post_money_is_an_error(record):
    record["rounds"][1]["postMoney"] = 9999
    assert any("post-money" in e for e in validate_company(record))


def test_currency_must_appear_in_the_quote(record):
    record["valuation"]["currency"] = "USD"     # the quote says euros
    assert any("quote" in e for e in validate_company(record))


def test_a_non_breaking_space_in_the_quote_still_matches(record):
    # Replace normal spaces with non-breaking spaces in "1.2 billion"
    nbsp = chr(0xa0)
    record["sources"][0]["quote"] = record["sources"][0]["quote"].replace(
        "1.2 billion", f"1.2{nbsp}billion")
    assert validate_company(record) == []


def test_null_sectors_is_an_error(record):
    record["sectors"] = None
    assert any("sectors" in e for e in validate_company(record))


def test_empty_sectors_is_an_error(record):
    record["sectors"] = []
    assert any("sectors" in e for e in validate_company(record))


def test_hq_missing_city_is_an_error(record):
    del record["hq"]["city"]
    assert any("hq.city" in e for e in validate_company(record))


def test_founded_year_as_a_string_is_an_error(record):
    record["foundedYear"] = "2015"
    assert any("foundedYear" in e for e in validate_company(record))


def test_a_well_formed_disputed_valuation_validates(record):
    record["valuation"]["disputed"] = {
        "note": "A later filing put the round at €900m post-money.", "source": "s2"}
    assert validate_company(record) == []


def test_disputed_citing_an_unknown_source_is_an_error(record):
    record["valuation"]["disputed"] = {"note": "Conflicting figure reported.", "source": "s99"}
    assert any("disputed" in e and "s99" in e for e in validate_company(record))


def test_disputed_with_an_empty_note_is_an_error(record):
    record["valuation"]["disputed"] = {"note": "  ", "source": "s2"}
    assert any("disputed.note" in e for e in validate_company(record))


def test_a_well_formed_also_based_in_validates(record):
    record["alsoBasedIn"] = ["New York"]
    assert validate_company(record) == []


def test_also_based_in_with_a_blank_entry_is_an_error(record):
    record["alsoBasedIn"] = ["New York", "  "]
    assert any("alsoBasedIn" in e for e in validate_company(record))


def test_also_based_in_that_is_not_a_list_is_an_error(record):
    record["alsoBasedIn"] = "New York"
    assert any("alsoBasedIn" in e for e in validate_company(record))


def test_a_round_that_crossed_the_threshold_earlier_contradicts_becameUnicorn(record):
    """The Celonis shape: every figure sourced, every quote honest, and becameUnicorn
    still naming a later round than the one that actually crossed $1bn. Nothing else
    in the validator compares rounds to each other, so nothing else catches it."""
    record["rounds"][0]["postMoney"] = 1000
    record["sources"][1]["quote"] = (
        "Example GmbH raised 60 million euros in a Series B round led by Earlybird "
        "on a 1 billion euro valuation.")
    errors = validate_company(record)
    assert any("crossed earlier" in e and "r1" in e and "r2" in e for e in errors)


def test_repointing_becameUnicorn_at_the_earlier_round_clears_it(record):
    record["rounds"][0]["postMoney"] = 1000
    record["sources"][1]["quote"] = (
        "Example GmbH raised 60 million euros in a Series B round led by Earlybird "
        "on a 1 billion euro valuation.")
    record["becameUnicorn"] = {"date": "2021-05", "roundId": "r1", "source": "s2"}
    assert validate_company(record) == []


def test_a_later_round_over_the_threshold_is_not_an_earlier_crossing(record):
    """The ordinary case every record here has: rounds after the unicorn round are
    naturally over the threshold too, and must not be reported."""
    assert validate_company(record) == []


def test_a_well_formed_disputed_round_amount_validates(record):
    record["rounds"][1]["disputed"] = {
        "note": "Other outlets report this round as 100 million euros.", "source": "s2"}
    assert validate_company(record) == []


def test_disputed_round_citing_an_unknown_source_is_an_error(record):
    record["rounds"][1]["disputed"] = {"note": "Conflicting figure reported.", "source": "s99"}
    assert any("round r2" in e and "disputed" in e and "s99" in e
               for e in validate_company(record))


def test_disputed_round_with_an_empty_note_is_an_error(record):
    record["rounds"][1]["disputed"] = {"note": "", "source": "s2"}
    assert any("round r2" in e and "disputed.note" in e for e in validate_company(record))
