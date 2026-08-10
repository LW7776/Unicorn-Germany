# tests/test_weekly_funding.py
#
# What this module still does: it gathers a week of German funding candidates
# for a person to write up. What it no longer does: call a model, assemble a
# week file, or publish anything. The tests for those went with the code.
import datetime as dt

import pytest

from tools.weekly_funding import (
    candidates, collect, known_companies, last_complete_week, read_amount,
    read_company, read_headline, tracked_in)

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


def test_the_body_text_is_carried_through_for_the_person_writing_the_week():
    """The issue links the article, but whoever drafts the week works from the
    reporting. Carrying the body through is what makes that possible without a
    second fetch."""
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


# --- reading a headline -----------------------------------------------------
#
# The bar these tests hold the reader to is not recall. It is that every field
# it emits can be pointed at in the headline beside it, and that a headline it
# cannot read cleanly is annotated with nothing rather than with a guess.

def an_article(title, **overrides):
    entry = {
        "id": "a1", "publication": "Tech.eu", "title": title,
        "url": "https://tech.eu/2026/07/22/x/", "publishedOn": "2026-07-22",
        "text": "",
    }
    entry.update(overrides)
    return entry


@pytest.mark.parametrize("headline,expected", [
    ("Beispiel raises €12 million", (12.0, "EUR")),
    ("Beispiel raises €12M in Series A", (12.0, "EUR")),
    ("Beispiel raises $50 million", (50.0, "USD")),
    ("Beispiel raises $1.2bn at a new valuation", (1200.0, "USD")),
    ("Beispiel raises EUR 7.5 million", (7.5, "EUR")),
    ("Beispiel sammelt 50 Millionen Euro ein", (50.0, "EUR")),
    ("Beispiel sammelt 1,2 Milliarden Euro ein", (1200.0, "EUR")),
    ("Beispiel raises 30 million euros", (30.0, "EUR")),
])
def test_a_figure_is_read_in_both_word_orders_and_both_languages(headline, expected):
    assert read_amount(headline) == expected


@pytest.mark.parametrize("headline", [
    "Beispiel raises €12",                 # no scale word: 12 what?
    "Beispiel raises 12 million",          # no currency
    "Beispiel raises a Series A round",    # no figure at all
    "Beispiel raises £12 million",         # a currency this site cannot render
])
def test_an_unreadable_figure_yields_nothing_rather_than_a_guess(headline):
    assert read_amount(headline) is None


@pytest.mark.parametrize("headline,company,hq", [
    ("Berlin-based Beispiel raises €12 million", "Beispiel", "Berlin"),
    ("Munich's Beispiel GmbH secures $20 million", "Beispiel GmbH", "Munich"),
    ("German AI startup Beispiel lands €9m seed", "Beispiel", None),
    ("Beispiel raises €12 million", "Beispiel", None),
    ("Hamburg-based fintech Beispiel Bank closes €30M Series B",
     "Beispiel Bank", "Hamburg"),
    ("Exclusive: Berlin-based Beispiel raises €12 million", "Beispiel", "Berlin"),
    # The auxiliary belongs to the verb, not to the name.
    ("Beispiel has raised €12 million", "Beispiel", None),
    ("Berlin-based Beispiel just closed a €12M round", "Beispiel", "Berlin"),
])
def test_the_company_is_what_stands_between_the_framing_and_the_verb(
        headline, company, hq):
    assert read_company(headline) == (company, hq)


@pytest.mark.parametrize("headline", [
    "The startup raises €12 million",                    # no name survives the strip
    "Beispiel is a Berlin company with €12 million",     # no raise verb
    "A very long run of words that is plainly a sentence and not a company name at all raises €12 million",
])
def test_a_headline_with_no_readable_company_is_dropped(headline):
    assert read_company(headline)[0] is None


@pytest.mark.parametrize("headline", [
    "Some VC closes €200 million fund IV",
    "Beispiel is in talks to raise €12 million",
    "Beispiel reportedly raises €12 million",
    "Grosse AG acquires Beispiel for €12 million",
    "Beispiel raises €12 million ahead of its IPO",
])
def test_what_is_not_a_closed_round_is_not_read_as_one(headline):
    assert read_headline(an_article(headline)) is None


def test_a_read_round_carries_a_company_a_figure_and_a_stage():
    entry = read_headline(an_article(
        "Berlin-based Beispiel raises €12 million in a Series A"))
    assert entry["company"] == "Beispiel"
    assert (entry["amount"], entry["currency"]) == (12.0, "EUR")
    assert entry["hq"] == "Berlin" and entry["stage"] == "Series A"


def test_a_loose_figure_is_marked_approximate_rather_than_stated_flat():
    entry = read_headline(an_article("Beispiel raises over €10 million"))
    assert entry["approximate"] is True
    assert read_headline(an_article("Beispiel raises €10 million"))["approximate"] is False


# --- the register cross-check ------------------------------------------------

def test_a_company_already_in_the_register_is_recognised(tmp_path):
    (tmp_path / "beispiel.json").write_text(
        '{"slug": "beispiel", "name": "Beispiel"}', encoding="utf-8")
    known = known_companies(str(tmp_path))
    assert tracked_in("Berlin-based Beispiel raises €12 million", known) == "beispiel"
    assert tracked_in("Anderswo raises €12 million", known) is None


def test_a_short_tracked_name_does_not_match_inside_a_longer_word(tmp_path):
    """The same word-boundary rule tools/watch.py applies, and for the same
    reason: a tracked company called Flix must not be flagged by every FlixBus
    headline, because noise is what makes a person stop reading the issue."""
    (tmp_path / "flix.json").write_text(
        '{"slug": "flix", "name": "Flix"}', encoding="utf-8")
    known = known_companies(str(tmp_path))
    assert tracked_in("FlixBus raises €12 million", known) is None
    assert tracked_in("Flix raises €12 million", known) == "flix"


# --- the week, as the Monday issue needs it ---------------------------------

def test_a_readable_round_is_separated_from_the_rest_of_the_week(tmp_path):
    report = candidates(
        "2026-W30", feeds={"Tech.eu": "https://tech.eu/feed/"},
        fetcher=stub([feed(
            GERMAN_ROUND,
            item("German startups had a busy week of funding",
                 "https://tech.eu/2026/07/23/roundup/",
                 "Thu, 23 Jul 2026 09:00:00 GMT",
                 "<p>A Berlin round, a Munich seed, and more funding besides.</p>"))]),
        companies_dir=str(tmp_path))
    assert [r["company"] for r in report["rounds"]] == ["Beispiel"]
    assert [o["headline"] for o in report["other"]] == [
        "German startups had a busy week of funding"]
    assert report["week"] == "2026-W30"
    assert (report["start"], report["end"]) == ("2026-07-20", "2026-07-26")


def test_the_biggest_round_is_listed_first(tmp_path):
    report = candidates(
        "2026-W30", feeds={"Tech.eu": "https://tech.eu/feed/"},
        fetcher=stub([feed(
            GERMAN_ROUND,
            item("Munich's Zweitens secures $30 million",
                 "https://tech.eu/2026/07/23/zweitens/",
                 "Thu, 23 Jul 2026 09:00:00 GMT",
                 "<p>Zweitens, a Munich company, raised $30 million.</p>"))]),
        companies_dir=str(tmp_path))
    assert [r["company"] for r in report["rounds"]] == ["Zweitens", "Beispiel"]


def test_two_publications_on_one_round_leave_one_round_to_write_up(tmp_path):
    """The duplicate is not thrown away — the second write-up is often the
    better-sourced one — but it stops being a second thing to write."""
    report = candidates(
        "2026-W30",
        feeds={"Sifted": "https://sifted.eu/feed", "Tech.eu": "https://tech.eu/feed/"},
        fetcher=lambda url: feed(GERMAN_ROUND) if "tech.eu" in url else feed(item(
            "Beispiel raises €12M in Series A",
            "https://sifted.eu/2026/07/22/beispiel/",
            "Tue, 22 Jul 2026 09:00:00 GMT",
            "<p>Beispiel, of Berlin, raised €12 million.</p>")),
        companies_dir=str(tmp_path))
    assert len(report["rounds"]) == 1
    assert len(report["other"]) == 1


def test_a_round_for_a_tracked_company_is_flagged(tmp_path):
    (tmp_path / "beispiel.json").write_text(
        '{"slug": "beispiel", "name": "Beispiel"}', encoding="utf-8")
    report = candidates("2026-W30", feeds={"Tech.eu": "https://tech.eu/feed/"},
                        fetcher=stub([feed(GERMAN_ROUND)]),
                        companies_dir=str(tmp_path))
    assert report["rounds"][0]["tracked"] == "beispiel"


def test_a_quiet_week_reports_nothing_rather_than_failing(tmp_path):
    """The workflow turns an empty scan into "open no issue". Nothing here
    raises, and nothing here is a failure: a week with no German rounds is a
    real outcome."""
    report = candidates("2026-W30", feeds={"Tech.eu": "https://tech.eu/feed/"},
                        fetcher=stub([feed(NOT_FUNDING)]),
                        companies_dir=str(tmp_path))
    assert report["rounds"] == [] and report["other"] == []
    assert report["feedErrors"] == []


def test_a_dead_feed_is_reported_in_the_week(tmp_path):
    def broken(url):
        raise OSError("connection reset")
    report = candidates("2026-W30", feeds={"Tech.eu": "https://tech.eu/feed/"},
                        fetcher=broken, companies_dir=str(tmp_path))
    assert report["feedsTried"] == 1
    assert len(report["feedErrors"]) == 1
