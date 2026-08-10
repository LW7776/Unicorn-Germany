"""The About page states numbers. They have to be the data's numbers.

about.html carries the current twelve-month unicorn count, the register's size and
the disclosed FX rate as its own text, so a reader with JavaScript off (and the
single-file demo bundle, which never runs static-page.js) sees the right figures.
assets/js/static-page.js overwrites all four at runtime from data/companies.json
and data/fx.json, which means the authored copy can go stale without anything
visibly breaking. That is exactly the failure a test is for.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ABOUT = ROOT / "about.html"

# <span class="qa__figure" data-stat="new12">11</span>
PLACEHOLDER = re.compile(
    r'<span class="qa__figure" data-(stat|fx)="([\w-]+)">([^<]*)</span>')


def _authored():
    return {
        f"{kind}:{key}": value
        for kind, key, value in PLACEHOLDER.findall(ABOUT.read_text(encoding="utf-8"))
    }


def test_every_authored_figure_matches_the_data_it_describes():
    stats = json.loads((ROOT / "data" / "companies.json").read_text(encoding="utf-8"))["stats"]
    fx = json.loads((ROOT / "data" / "fx.json").read_text(encoding="utf-8"))
    authored = _authored()

    assert authored == {
        "stat:new12": str(stats["newInLast12Months"]),
        "stat:count": str(stats["count"]),
        "fx:rate": str(fx["USD_EUR"]),
        "fx:asof": str(fx["asOf"]),
    }


def test_the_answers_are_disclosure_widgets_and_not_hand_rolled():
    """Native <details>/<summary> is the whole accessibility story here. A future
    edit that swaps in a div-and-aria-expanded pattern loses keyboard operation,
    the announced expandable role and the no-JavaScript reading, all at once."""
    html = ABOUT.read_text(encoding="utf-8")
    rows = html.count('<details class="qa__row"')
    assert rows == html.count('<summary class="qa__q">') == 9
    assert 'aria-expanded' not in html


def test_exactly_one_phrase_on_the_site_carries_the_gradient():
    """docs/BRAND.md gives the gradient to one phrase at a time, and DESIGN.md's
    "one bold element per screen" is the reason. It is a signature while it is
    rare and a habit the moment it is not, and nothing about the CSS itself stops
    a second one being added, so this is the thing that does.

    The phrase is `Built by startups.` in the Companies intro (.intro__accent).
    A gradient set in type is `background-clip: text`, prefixed or not, so
    counting the unprefixed property counts the rules regardless of prefixing."""
    css = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "assets" / "css").glob("*.css")))
    # Comments out first: this file's own rule is explained in a comment that
    # names the property, and a test that counts its own documentation passes
    # for the wrong reason.
    declarations = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    # The lookbehind is what keeps the -webkit- prefix from being counted as a
    # second phrase: a prefixed and unprefixed pair is one declaration written
    # twice for Safari, not two tinted phrases.
    tinted = re.findall(r"(?<!-)\bbackground-clip\s*:\s*text", declarations)
    assert len(tinted) == 1, f"expected one gradient-tinted phrase, found {len(tinted)}"
    assert ".intro__accent" in declarations
