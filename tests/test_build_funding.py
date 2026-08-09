# tests/test_build_funding.py
import json
import pathlib

import pytest

from tools.build import build_funding, derive_round, derive_week, format_names, format_range

REPO = pathlib.Path(__file__).parent.parent


def a_round(**overrides):
    entry = {
        "id": "m1", "company": "Example GmbH", "hq": "Berlin", "stage": "Series A",
        "amount": 12.5, "currency": "EUR", "approximate": False,
        "valuation": None, "valuationCurrency": None,
        "founders": ["Ada Beispiel", "Bruno Beispiel"], "investors": ["Some Fund"],
        "source": {"publication": "Tech.eu", "title": "t",
                   "url": "https://tech.eu/x/", "publishedOn": "2026-07-22"},
    }
    entry.update(overrides)
    return entry


def test_amount_labels_use_the_registers_own_formatter():
    derived = derive_round(a_round(amount=13.1))
    assert derived["amountLabel"] == "€13.1 m"
    assert derive_round(a_round(amount=3.2, currency="USD"))["amountLabel"] == "$3.2 m"
    assert derive_round(a_round(amount=10, approximate=True))["amountLabel"] == "~€10 m"


def test_a_valuation_renders_in_its_own_currency():
    derived = derive_round(a_round(valuation=1000, valuationCurrency="EUR"))
    assert derived["valuationLabel"] == "€1 bn"


def test_no_valuation_means_no_label_rather_than_a_dash():
    """The owner's format puts the valuation in parentheses; "(at a — valuation)"
    is worse than no parenthetical, so the renderer omits the clause."""
    assert derive_round(a_round())["valuationLabel"] is None


def test_founders_are_joined_for_the_owners_sentence():
    assert format_names(["A"]) == "A"
    assert format_names(["A", "B"]) == "A and B"
    assert format_names(["A", "B", "C"]) == "A, B and C"


def test_an_unnamed_founder_list_produces_no_label_not_an_invented_one():
    assert format_names([]) is None
    assert derive_round(a_round(founders=[]))["foundersLabel"] is None


def test_week_ranges_collapse_a_shared_month_and_spell_out_a_crossing():
    assert format_range("2026-07-20", "2026-07-26") == "20–26 Jul 2026"
    assert format_range("2026-07-27", "2026-08-02") == "27 Jul – 2 Aug 2026"
    assert format_range("2026-12-28", "2027-01-03") == "28 Dec 2026 – 3 Jan 2027"


def test_week_derivation_precomputes_every_label_the_browser_needs():
    week = derive_week({
        "week": "2026-W30", "start": "2026-07-20", "end": "2026-07-26",
        "lead": [dict(a_round(id="l1"), text="Prose.")],
        "more": [a_round(), a_round(id="m2")],
    })
    assert week["shortLabel"] == "W30"
    assert week["yearLabel"] == "2026"
    assert week["rangeLabel"] == "20–26 Jul 2026"
    assert week["roundCount"] == 3
    assert week["moreCount"] == 2
    assert week["lead"][0]["source"]["publishedLabel"] == "22 Jul 2026"


def test_weeks_are_ordered_newest_first(tmp_path):
    for week_id, monday, sunday in (("2026-W30", "2026-07-20", "2026-07-26"),
                                    ("2026-W32", "2026-08-03", "2026-08-09"),
                                    ("2026-W31", "2026-07-27", "2026-08-02")):
        (tmp_path / f"{week_id}.json").write_text(json.dumps({
            "week": week_id, "start": monday, "end": sunday,
            "lead": [dict(a_round(id="l1"), text="Prose.")], "more": [],
        }), encoding="utf-8")
    payload = build_funding(src=str(tmp_path), out=str(tmp_path / "out.json"))
    assert [w["week"] for w in payload["weeks"]] == ["2026-W32", "2026-W31", "2026-W30"]
    assert payload["stats"]["latestWeek"] == "2026-W32"


def test_ordering_never_consults_the_wall_clock(tmp_path):
    """A week dated in the future still sorts newest — "newest" is a fact about
    the files, so CI can diff the generated payload on any day it happens to run."""
    for week_id, monday, sunday in (("2026-W30", "2026-07-20", "2026-07-26"),
                                    ("2099-W01", "2099-01-05", "2099-01-11")):
        (tmp_path / f"{week_id}.json").write_text(json.dumps({
            "week": week_id, "start": monday, "end": sunday,
            "lead": [dict(a_round(id="l1"), text="Prose.")], "more": [],
        }), encoding="utf-8")
    payload = build_funding(src=str(tmp_path), out=str(tmp_path / "out.json"))
    assert payload["weeks"][0]["week"] == "2099-W01"


def test_the_build_is_deterministic(tmp_path):
    first = build_funding(out=str(tmp_path / "a.json"))
    second = build_funding(out=str(tmp_path / "b.json"))
    assert (tmp_path / "a.json").read_text() == (tmp_path / "b.json").read_text()
    assert first == second


def test_the_committed_payload_matches_the_source_files(tmp_path):
    """The same guarantee CI enforces: data/funding.json is generated, never edited."""
    fresh = build_funding(out=str(tmp_path / "funding.json"))
    committed = json.loads((REPO / "data" / "funding.json").read_text(encoding="utf-8"))
    assert fresh == committed


def test_an_empty_directory_produces_an_empty_payload(tmp_path):
    payload = build_funding(src=str(tmp_path), out=str(tmp_path / "out.json"))
    assert payload["weeks"] == []
    assert payload["stats"] == {"weekCount": 0, "roundCount": 0, "latestWeek": None}
