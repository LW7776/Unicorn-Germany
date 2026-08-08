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


def test_format_amount_keeps_a_two_decimal_billion_figure():
    """A $3.25bn valuation must not print as "$3.2 bn".

    That was a real published defect: f"{3.25:.1f}" is "3.2", because Python
    rounds half-to-even, so the register understated Black Forest Labs by $50m
    on its own card while the quote beside it read "$3.25 billion".
    """
    assert format_amount(3250, "USD", False) == "$3.25 bn"
    assert format_amount(3250, "USD", True) == "~$3.25 bn"


@pytest.mark.parametrize("millions, expected", [
    (3250, "$3.25 bn"),   # .1f gave "3.2" — half-to-even rounded down
    (1250, "$1.25 bn"),   # .1f gave "1.2" — same, and 1.25 is exact in binary
    (1750, "$1.75 bn"),
])
def test_a_half_boundary_is_no_longer_rounded_away(millions, expected):
    assert format_amount(millions, "USD", False) == expected


def test_format_amount_uses_as_many_decimals_as_the_value_needs():
    assert format_amount(1075, "USD", False) == "$1.075 bn"
    assert format_amount(1234.5, "EUR", False) == "€1.2345 bn"


@pytest.mark.parametrize("millions, currency, expected", [
    (13000, "USD", "$13 bn"),
    (18000, "USD", "$18 bn"),
    (1400, "EUR", "€1.4 bn"),
    (12500, "EUR", "€12.5 bn"),
    (1000, "EUR", "€1 bn"),
    (10000, "USD", "$10 bn"),     # the trailing zero is significant, not padding
    (20000, "EUR", "€20 bn"),
    (100000, "USD", "$100 bn"),
])
def test_whole_and_one_decimal_billions_render_exactly_as_before(millions, currency, expected):
    """Every label the register already published must be byte-identical.

    The multiples of ten pin the guard in _trim_zeros: a bare rstrip("0") on
    "100" yields "1", which would be a hundredfold error rather than a
    rounding one.
    """
    assert format_amount(millions, currency, False) == expected


def test_format_amount_keeps_a_fractional_sub_billion_decimal():
    """A €102.5m round must not print as "€102 m" — that is a figure no source stated."""
    assert format_amount(102.5, "EUR", False) == "€102.5 m"
    assert format_amount(27.5, "USD", True) == "~$27.5 m"


def test_format_amount_is_unchanged_for_whole_sub_billion_amounts():
    assert format_amount(850, "EUR", True) == "~€850 m"
    assert format_amount(120, "USD", False) == "$120 m"
    assert format_amount(50, "USD", False) == "$50 m"
    assert format_amount(850.0, "EUR", True) == "~€850 m"


def test_fractional_millions_are_recognised_in_english_and_german_forms():
    assert quote_states_figure("a previous Series A of 102.5 million euros", 102.5, "EUR")
    assert quote_states_figure("eine Series A über 102,5 Millionen Euro", 102.5, "EUR")
    assert quote_states_figure("a Series A of $27.5 million in June 2016", 27.5, "USD")


def test_a_fractional_amount_does_not_match_its_truncated_neighbour():
    """102.5 and 102 are different numbers; the digit boundary must keep them apart."""
    assert not quote_states_figure("a Series A of 102 million euros", 102.5, "EUR")


def test_whole_sub_billion_matching_is_unchanged():
    assert quote_states_figure("a Series B of $50 million in June 2018", 50, "USD")
    assert not quote_states_figure("a Series B of $50.5 million", 50, "USD")


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
    assert quote_states_figure("a $3.25 billion post-money valuation", 3250, "USD")


def test_a_three_decimal_billion_figure_is_recognised():
    """Quantising only to two and one places left this unmatchable.

    1075 generated {"1.08", "1.1"} and nothing else, so a source stating the
    exact figure failed the quote check — and the exact figure is now also what
    format_amount prints. The renderer and the matcher have to agree, or a
    round that is properly sourced still cannot be published.
    """
    assert quote_states_figure("raised at a $1.075 billion valuation", 1075, "USD")
    assert quote_states_figure("mit 1,075 Milliarden Euro bewertet", 1075, "EUR")


def test_a_source_that_rounds_to_one_decimal_still_matches():
    """Adding the exact form must not cost us the rounded ones sources use."""
    assert quote_states_figure("valued at about $3.3 billion", 3250, "USD")
    assert quote_states_figure("rund 3,3 Milliarden Euro", 3250, "EUR")


def test_a_whole_billion_approximation_does_not_satisfy_a_precise_record():
    """"$3 billion" is not evidence for a $3.25bn figure.

    Forms are quantised to two and one places, never to none, so a vaguer
    sentence cannot stand in for a precise record — the same digit-boundary
    discipline that keeps "102 million" from satisfying a €102.5m round.
    """
    assert not quote_states_figure("valued at roughly $3 billion", 3250, "USD")
    assert not quote_states_figure("worth about $1 billion", 1075, "USD")


def test_whole_ten_billion_figures_are_recognised():
    assert quote_states_figure("now worth $10 billion", 10000, "USD")
    assert quote_states_figure("a €100 billion market", 100000, "EUR")


@pytest.mark.parametrize("millions, currency", [
    (3250, "USD"), (1075, "USD"), (13000, "USD"), (1400, "EUR"),
    (10000, "USD"), (12500, "EUR"), (1000, "EUR"),
])
def test_the_rendered_label_is_itself_a_quotable_form(millions, currency):
    """The register's own label must satisfy its own matcher.

    If format_amount can print a number that quote_states_figure would reject,
    the two halves of this module disagree about what the figure looks like —
    which is exactly the gap that made a $3.25bn round unpublishable.
    """
    label = format_amount(millions, currency, False)
    assert quote_states_figure(f"valued at {label}", millions, currency)


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
