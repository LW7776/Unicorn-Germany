# tests/test_weekly_funding.py
import datetime as dt

import pytest

from tools.validate_funding import validate_week
from tools.weekly_funding import (
    assemble, collect, last_complete_week, states_figure, tracked_companies, verify)

ITEM_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel>{items}</channel></rss>"""

ITEM = """<item>
  <title>{title}</title>
  <link>{link}</link>
  <pubDate>{pub}</pubDate>
  <content:encoded><![CDATA[{body}]]></content:encoded>
</item>"""


def feed(*items):
    return ITEM_TEMPLATE.format(items="".join(items))


def item(title, link, pub, body=""):
    return ITEM.format(title=title, link=link, pub=pub, body=body)


GERMAN_ROUND = item(
    "Berlin-based Beispiel raises €12 million Series A",
    "https://tech.eu/2026/07/22/beispiel/",
    "Tue, 22 Jul 2026 09:00:00 GMT",
    "<p>Beispiel, a Berlin-based startup, has raised €12 million in a Series A "
    "led by Some Fund. Founded in 2021 by Ada Beispiel and Bruno Muster.</p>")

FRENCH_ROUND = item(
    "Paris-based Exemple raises €30 million",
    "https://tech.eu/2026/07/22/exemple/",
    "Tue, 22 Jul 2026 09:00:00 GMT",
    "<p>Exemple, a Paris company, raised €30 million.</p>")

OUT_OF_WEEK = item(
    "Munich-based Spaeter raises €9 million seed",
    "https://tech.eu/2026/08/05/spaeter/",
    "Wed, 05 Aug 2026 09:00:00 GMT",
    "<p>Spaeter, a Munich startup, raised €9 million.</p>")

NOT_FUNDING = item(
    "Berlin design tips for founders",
    "https://tech.eu/2026/07/22/design/",
    "Tue, 22 Jul 2026 09:00:00 GMT",
    "<p>Some thoughts about German design.</p>")


def stub(pages):
    """A fetcher returning a different document per requested page."""
    def fetcher(url):
        page = 1
        if "paged=" in url:
            page = int(url.split("paged=")[1])
        if page > len(pages):
            return feed()
        return pages[page - 1]
    return fetcher


# --- which week a Monday run covers ----------------------------------------

def test_the_run_covers_the_week_that_just_ended():
    # Monday 10 Aug 2026 -> the week of 3-9 Aug, not the one it stands in.
    assert last_complete_week(dt.date(2026, 8, 10)) == "2026-W32"
    assert last_complete_week(dt.date(2026, 8, 3)) == "2026-W31"


def test_the_week_boundary_holds_across_a_year_end():
    # Monday 4 Jan 2027 -> the ISO week that ended Sunday 3 Jan, which is 2026-W53.
    assert last_complete_week(dt.date(2027, 1, 4)) == "2026-W53"


# --- collecting -------------------------------------------------------------

def test_only_articles_published_inside_the_week_are_collected():
    articles, errors = collect(
        "2026-W30", feeds={"Tech.eu": "https://tech.eu/feed/"},
        fetcher=stub([feed(GERMAN_ROUND, OUT_OF_WEEK)]))
    assert errors == []
    assert [a["title"] for a in articles] == [
        "Berlin-based Beispiel raises €12 million Series A"]


def test_a_round_with_no_german_signal_is_not_collected():
    articles, _ = collect("2026-W30", feeds={"Tech.eu": "https://tech.eu/feed/"},
                          fetcher=stub([feed(FRENCH_ROUND)]))
    assert articles == []


def test_an_article_with_no_funding_signal_is_not_collected():
    articles, _ = collect("2026-W30", feeds={"Tech.eu": "https://tech.eu/feed/"},
                          fetcher=stub([feed(NOT_FUNDING)]))
    assert articles == []


def test_the_body_text_is_carried_through_for_verification():
    articles, _ = collect("2026-W30", feeds={"Tech.eu": "https://tech.eu/feed/"},
                          fetcher=stub([feed(GERMAN_ROUND)]))
    assert "Ada Beispiel" in articles[0]["text"]
    assert "<p>" not in articles[0]["text"]


def test_later_feed_pages_are_walked_so_a_monday_run_still_sees_tuesday():
    """A feed's front page holds about ten items; without paging, the earlier
    half of the week is simply invisible to a Monday run."""
    articles, _ = collect(
        "2026-W30", feeds={"Tech.eu": "https://tech.eu/feed/"},
        fetcher=stub([feed(OUT_OF_WEEK), feed(GERMAN_ROUND)]))
    assert [a["title"] for a in articles] == [
        "Berlin-based Beispiel raises €12 million Series A"]


def test_a_feed_that_ignores_paging_is_not_read_twice():
    """A feed that returns page one for every request must not produce
    duplicates — the walk stops as soon as a page adds nothing new."""
    articles, _ = collect("2026-W30", feeds={"Tech.eu": "https://tech.eu/feed/"},
                          fetcher=lambda url: feed(GERMAN_ROUND))
    assert len(articles) == 1


def test_a_dead_feed_is_an_error_not_an_exception():
    def broken(url):
        raise OSError("connection reset")
    articles, errors = collect("2026-W30", feeds={"Tech.eu": "https://tech.eu/feed/"},
                               fetcher=broken)
    assert articles == []
    assert any("connection reset" in e for e in errors)


def test_one_dead_feed_does_not_cost_the_other_feeds():
    def mixed(url):
        if "sifted" in url:
            raise OSError("503")
        return feed(GERMAN_ROUND)
    articles, errors = collect(
        "2026-W30",
        feeds={"Sifted": "https://sifted.eu/feed", "Tech.eu": "https://tech.eu/feed/"},
        fetcher=mixed)
    assert len(articles) == 1
    assert any("Sifted" in e for e in errors)


def test_a_feed_off_the_allowlist_is_skipped_loudly():
    articles, errors = collect("2026-W30", feeds={"Some Blog": "https://blog/feed"},
                               fetcher=stub([feed(GERMAN_ROUND)]))
    assert articles == []
    assert any("not on the source allowlist" in e for e in errors)


# --- the guard that makes the prompt a rule ---------------------------------

@pytest.fixture
def articles():
    found, _ = collect("2026-W30", feeds={"Tech.eu": "https://tech.eu/feed/"},
                       fetcher=stub([feed(GERMAN_ROUND)]))
    return found


def a_draft(**overrides):
    entry = {
        "company": "Beispiel", "hq": "Berlin", "stage": "Series A",
        "amount": 12, "currency": "EUR", "approximate": False,
        "valuation": None, "valuationCurrency": None,
        "founders": ["Ada Beispiel", "Bruno Muster"], "investors": ["Some Fund"],
        "text": "A write-up.", "articleId": "a1",
    }
    entry.update(overrides)
    return entry


def test_a_faithful_draft_verifies(articles):
    assert verify([a_draft()], articles) == []


def test_an_invented_company_is_caught(articles):
    problems = verify([a_draft(company="Erfunden GmbH")], articles)
    assert any("company name does not appear" in p for p in problems)


def test_an_invented_founder_is_caught(articles):
    problems = verify([a_draft(founders=["Ada Beispiel", "Carla Erfunden"])], articles)
    assert any("Carla Erfunden" in p for p in problems)


def test_an_invented_amount_is_caught(articles):
    problems = verify([a_draft(amount=45)], articles)
    assert any("does not state the amount 45" in p for p in problems)


def test_an_invented_valuation_is_caught(articles):
    """A €1bn valuation is stored as 1000, whose billions form is the bare "1".
    A substring check would find that "1" inside "2021" or "€12 million" and
    wave the invented figure through, which is why this delegates to
    tools/schema.py's digit-boundary matcher instead."""
    problems = verify([a_draft(valuation=1000, valuationCurrency="EUR")], articles)
    assert any("does not state the valuation 1000" in p for p in problems)


def test_a_stated_valuation_verifies():
    found, _ = collect("2026-W30", feeds={"Tech.eu": "https://tech.eu/feed/"},
                       fetcher=stub([feed(item(
                           "Berlin-based Beispiel raises €12 million at a €1 billion valuation",
                           "https://tech.eu/2026/07/22/beispiel/",
                           "Tue, 22 Jul 2026 09:00:00 GMT",
                           "<p>Beispiel raised €12 million in a Series A at a €1 billion "
                           "valuation. Founded in 2021 by Ada Beispiel.</p>"))]))
    draft = a_draft(founders=["Ada Beispiel"], valuation=1000, valuationCurrency="EUR")
    assert verify([draft], found) == []


def test_a_citation_to_an_article_this_run_never_fetched_is_caught(articles):
    problems = verify([a_draft(articleId="a99")], articles)
    assert any("never fetched" in p for p in problems)


def test_a_founder_referred_to_by_surname_still_verifies(articles):
    """Articles introduce "Dr. Denis Kiefel" and then say "Kiefel"; rejecting a
    correctly-extracted name over a title would push the model toward dropping
    real founders, which is the opposite of what the guard is for."""
    assert verify([a_draft(founders=["Dr. Ada Beispiel"])], articles) == []


def test_billion_scale_amounts_match_how_an_article_writes_them():
    """The record stores 1200 for "$1.2 billion", so the check has to recognise
    the billions form or every large round would look invented."""
    assert states_figure("raised $1.2 billion in a Series D", 1200, "USD")
    assert states_figure("sammelte 1,2 Milliarden Euro ein", 1200, "EUR")
    assert states_figure("raised €13.1 million", 13.1, "EUR")


def test_a_bare_digit_inside_an_unrelated_number_does_not_count_as_a_figure():
    """The whole reason this delegates to tools/schema.py: "1" is a substring of
    "2021", and a €1bn valuation stored as 1000 has "1" as its billions form."""
    assert not states_figure("Founded in 2021, it raised €12 million", 1000, "EUR")


def test_the_currency_has_to_match_too():
    assert not states_figure("raised €12 million in a Series A", 12, "USD")


# --- assembling -------------------------------------------------------------

def test_assembled_weeks_pass_the_validator(articles):
    record = assemble("2026-W30", {"lead": [a_draft()], "more": [a_draft()]}, articles)
    assert validate_week(record) == []


def test_the_source_is_copied_from_the_fetch_not_from_the_model(articles):
    record = assemble("2026-W30", {"lead": [a_draft()], "more": []}, articles)
    source = record["lead"][0]["source"]
    assert source["url"] == "https://tech.eu/2026/07/22/beispiel/"
    assert source["publication"] == "Tech.eu"
    assert source["publishedOn"] == "2026-07-22"


def test_only_lead_rounds_carry_prose(articles):
    record = assemble("2026-W30", {"lead": [a_draft()], "more": [a_draft()]}, articles)
    assert record["lead"][0]["text"] == "A write-up."
    assert "text" not in record["more"][0]
    assert record["lead"][0]["id"] == "l1" and record["more"][0]["id"] == "m1"


# --- the register cross-link ------------------------------------------------

def test_a_company_already_in_the_register_is_flagged(articles, tmp_path):
    (tmp_path / "beispiel.json").write_text(
        '{"slug": "beispiel", "name": "Beispiel"}', encoding="utf-8")
    record = assemble("2026-W30", {"lead": [a_draft()], "more": []}, articles)
    hits = tracked_companies(record, companies_dir=str(tmp_path))
    assert [h["slug"] for h in hits] == ["beispiel"]


def test_an_untracked_company_is_not_flagged(articles, tmp_path):
    record = assemble("2026-W30", {"lead": [a_draft()], "more": []}, articles)
    assert tracked_companies(record, companies_dir=str(tmp_path)) == []
