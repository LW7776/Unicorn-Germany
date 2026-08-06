# tests/test_schema.py
import pytest
from tools.schema import (
    SOURCE_ALLOWLIST, parse_date, date_sort_key, format_date,
    format_amount, figure_variants, quote_states_figure,
)


def test_parse_date_accepts_year_and_month_precision():
    assert parse_date("2024-03") == (2024, 3)
    assert parse_date("2024") == (2024, 0)


@pytest.mark.parametrize("bad", ["2024-3", "March 2024", "2024-03-11", "", "24-03", "2024-00", "2024-13"])
def test_parse_date_rejects_other_shapes(bad):
    with pytest.raises(ValueError):
        parse_date(bad)


def test_year_precision_sorts_before_any_month_of_that_year():
    assert date_sort_key("2024") < date_sort_key("2024-01")
    assert date_sort_key("2023-12") < date_sort_key("2024")


def test_format_date_is_month_and_year_or_bare_year():
    assert format_date("2024-03") == "Mar 2024"
    assert format_date("2024") == "2024"


def test_format_amount_renders_billions_with_approximate_marker():
    assert format_amount(13000, "USD", True) == "~$13 bn"
    assert format_amount(1400, "EUR", True) == "~€1.4 bn"
    assert format_amount(2000, "EUR", False) == "€2 bn"
    assert format_amount(850, "EUR", True) == "~€850 m"


def test_figure_variants_cover_how_sources_write_the_number():
    assert "13" in figure_variants(13000)
    variants = figure_variants(1400)
    assert {"1.4", "1,4"} <= variants
    assert "850" in figure_variants(850)


def test_allowlist_excludes_licensed_databases():
    assert "Reuters" in SOURCE_ALLOWLIST
    assert "Sifted" in SOURCE_ALLOWLIST
    for banned in ("Crunchbase", "Dealroom", "PitchBook", "Tracxn", "Wikipedia"):
        assert banned not in SOURCE_ALLOWLIST


def test_two_decimal_billion_figures_are_recognised():
    assert quote_states_figure("valued at $1.25 billion", 1250, "USD")


def test_german_hyphenated_compound_is_recognised():
    assert quote_states_figure("die 1,4-Milliarden-Bewertung in Euro", 1400, "EUR")


def test_shorthand_b_suffix_is_recognised():
    assert quote_states_figure("now valued at $1.2B", 1200, "USD")


def test_a_bare_b_does_not_match_an_unrelated_german_word():
    assert not quote_states_figure("1,4 bis 2 Milliarden Euro erwartet", 1400, "EUR")


def test_a_space_thousands_separator_is_recognised():
    assert quote_states_figure("1 200 Millionen Euro", 1200, "EUR")


def test_the_scale_word_must_be_adjacent_to_the_number():
    assert not quote_states_figure("on 1 March, in euros", 1000, "EUR")


def test_hyphenated_english_phrasing_is_recognised():
    assert quote_states_figure("the round gave it a $1.2-billion valuation", 1200, "USD")
    assert quote_states_figure("the round was a $1.2-bn deal", 1200, "USD")


def test_clause_numbering_is_not_a_billion_figure():
    assert not quote_states_figure(
        "Gemaess Ziffer 1.2 b des Handelsregisterauszugs, EUR Stammkapital", 1200, "EUR")


def test_b2b_adjacency_is_not_a_billion_figure():
    assert not quote_states_figure(
        "the 1.2B2B focused fund invests in EUR-denominated startups", 1200, "EUR")


def test_section_numbering_is_not_a_billion_figure():
    assert not quote_states_figure(
        "per section 1.2b of the USD credit agreement filing", 1200, "USD")


def test_currency_attached_b_shorthand_is_still_recognised():
    assert quote_states_figure("now valued at $1.2B", 1200, "USD")


def test_german_hyphenated_compound_is_still_recognised():
    assert quote_states_figure("die 1,4-Milliarden-Bewertung in Euro", 1400, "EUR")


def test_a_spaced_b_after_a_currency_symbol_is_clause_lettering_not_a_figure():
    assert not quote_states_figure("Grundkapital € 1.2 b) der Satzung", 1200, "EUR")
    assert not quote_states_figure("See $1.2 b) of the credit agreement filing", 1200, "USD")
