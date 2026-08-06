import copy, json, pathlib, pytest
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


def test_valuation_predating_the_last_round_is_an_error(record):
    record["valuation"]["asOf"] = "2022-01"
    assert any("predates" in e for e in validate_company(record))


def test_unknown_unicorn_round_id_is_an_error(record):
    record["becameUnicorn"]["roundId"] = "r9"
    assert any("r9" in e for e in validate_company(record))


def test_slug_must_be_url_safe(record):
    record["slug"] = "Example GmbH"
    assert any("slug" in e for e in validate_company(record))
