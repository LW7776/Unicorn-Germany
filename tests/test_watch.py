import json, pathlib, pytest
from unittest.mock import patch
from tools.watch import parse_feed, match_candidates, scan, FUNDING_SIGNAL

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


def _item(title, source="Sifted"):
    return {"title": title, "link": "https://example.com/x", "published": "2024-03-13", "source": source}


ENGLISH_TITLES_BILLION_SCALE = [
    "Berlin startup reaches $10bn valuation after new round",
    "Munich fintech hits €25bn valuation",
    "Company X reaches $1.35bn valuation",
]

GERMAN_TITLES_FUNDING = [
    "Berliner Fintech sammelt 50 Millionen Euro in Serie-C-Runde ein",
    "Firma erreicht Milliarden-Bewertung nach neuer Runde",
    "Wefox schließt Finanzierungsrunde ab, Bewertung von 1 Milliarde Euro",
]


@pytest.mark.parametrize("title", ENGLISH_TITLES_BILLION_SCALE)
def test_any_billion_scale_valuation_is_a_new_candidate_not_only_exactly_1(title):
    """Finding 1: the old pattern only matched a valuation that literally started
    with the digit 1, so $10bn/€25bn/$1.35bn headlines were silently dropped."""
    hits = match_candidates([_item(title)], companies=[])
    assert any(h["company"] is None for h in hits), title


@pytest.mark.parametrize("title", GERMAN_TITLES_FUNDING)
def test_german_funding_vocabulary_is_recognised(title):
    """Finding 2: German headlines were invisible to FUNDING_SIGNAL — Gründerszene
    items only ever matched by accident, via the loanword 'Unicorn'."""
    assert FUNDING_SIGNAL.search(title), title


@pytest.mark.parametrize("title", GERMAN_TITLES_FUNDING[1:])
def test_german_billion_scale_headlines_are_new_candidates(title):
    hits = match_candidates([_item(title, source="Gründerszene")], companies=[])
    assert any(h["company"] is None for h in hits), title


def test_a_sub_billion_german_round_is_recognised_but_is_not_a_new_unicorn_candidate_on_its_own():
    """"Berliner Fintech sammelt 50 Millionen Euro ... ein" must no longer vanish
    silently (finding 2's German-vocabulary gap) — but on its own, sub-billion and
    naming no tracked company, it correctly produces no "new unicorn" candidate.
    That's finding 1's "do not widen to millions" guardrail doing its job, not a
    remaining bug. Paired with a tracked company, the same separable-verb
    construction ("sammelt ... ein") does surface as a tracked-company candidate.
    """
    title = "Berliner Fintech sammelt 50 Millionen Euro in Serie-C-Runde ein"
    assert FUNDING_SIGNAL.search(title)
    assert match_candidates([_item(title, source="Gründerszene")], companies=[]) == []

    tracked_title = "Flix sammelt 50 Millionen Euro in Serie-C-Runde ein"
    hits = match_candidates([_item(tracked_title, source="Gründerszene")],
                             companies=[{"name": "Flix", "slug": "flix"}])
    assert any(h["company"] == "flix" for h in hits)


ATOM_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Example Atom Feed</title>
  <entry>
    <title>Startup raises new funding round</title>
    <link href="https://example.com/atom-a" rel="alternate"/>
    <published>2024-03-13T09:00:00Z</published>
  </entry>
</feed>"""


def test_atom_feed_entries_are_parsed():
    """Finding 3: a feed that is well-formed XML but not RSS (e.g. Atom) must not
    silently parse to zero items."""
    items = parse_feed(ATOM_FIXTURE, source="TechCrunch")
    assert len(items) == 1
    assert items[0]["title"] == "Startup raises new funding round"
    assert items[0]["link"] == "https://example.com/atom-a"
    assert items[0]["published"] == "2024-03-13"
    assert items[0]["source"] == "TechCrunch"


NON_FEED_XML = """<?xml version="1.0" encoding="UTF-8"?>
<maintenance><message>Service temporarily unavailable</message></maintenance>"""


def test_a_well_formed_non_feed_document_yields_a_feed_error_not_a_silent_empty_scan(tmp_path):
    """Finding 3: a WAF/maintenance page or schema change that is still well-formed
    XML parses to zero items without raising — scan() must record that as a
    feedErrors entry rather than let it look like a quiet month."""
    out = tmp_path / "candidates.json"
    with patch("tools.watch.fetch", return_value=NON_FEED_XML):
        result = scan(feeds={"Sifted": "https://example.com/feed"}, companies=[], out=str(out))
    assert result["candidates"] == []
    assert any("Sifted" in e and "no items" in e for e in result["feedErrors"])
