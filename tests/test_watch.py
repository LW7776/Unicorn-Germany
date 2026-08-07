import json, pathlib, pytest
from tools.watch import parse_feed, match_candidates

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


@pytest.fixture
def items():
    return parse_feed((FIXTURES / "feed.xml").read_text(encoding="utf-8"), source="Sifted")


@pytest.fixture
def companies():
    return [json.loads((FIXTURES / "valid_company.json").read_text(encoding="utf-8"))]


def test_parse_feed_reads_title_link_and_date(items):
    assert len(items) == 3
    assert items[0]["title"].startswith("Example GmbH raises")
    assert items[0]["link"] == "https://sifted.eu/a"
    assert items[0]["published"] == "2024-03-13"
    assert items[0]["source"] == "Sifted"


def test_an_article_naming_a_tracked_company_is_a_candidate(items, companies):
    hits = match_candidates(items, companies)
    assert any(h["company"] == "example-gmbh" and "raises" in h["reason"] for h in hits)


def test_an_unknown_company_crossing_a_billion_is_a_new_candidate(items, companies):
    hits = match_candidates(items, companies)
    assert any(h["company"] is None and "Neuestern" in h["title"] for h in hits)


def test_an_article_with_no_funding_signal_is_ignored(items, companies):
    hits = match_candidates(items, companies)
    assert not any("design tips" in h["title"] for h in hits)


def test_short_company_name_does_not_match_inside_a_longer_word():
    """A tracked company named 'Flix' must not be flagged by an article about
    'FlixBus' — a naive substring check would produce noise every month."""
    companies = [{"name": "Flix", "slug": "flix"}]
    items = [{
        "title": "FlixBus raises funding round to expand across Europe",
        "link": "https://example.com/flixbus",
        "published": "2024-03-13",
        "source": "Sifted",
    }]
    hits = match_candidates(items, companies)
    assert not any(h["company"] == "flix" for h in hits)


def test_short_company_name_matches_as_a_standalone_word():
    companies = [{"name": "Flix", "slug": "flix"}]
    items = [{
        "title": "Flix raises new funding round to expand across Europe",
        "link": "https://example.com/flix",
        "published": "2024-03-13",
        "source": "Sifted",
    }]
    hits = match_candidates(items, companies)
    assert any(h["company"] == "flix" for h in hits)
