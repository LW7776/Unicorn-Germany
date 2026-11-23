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


def test_every_answer_on_the_about_page_is_readable_without_script():
    """The old About hid each answer behind <details>, and this test guarded that pattern.

    Aurora prints every answer open, which is what the copy rules ask for and which is strictly
    better for the thing the old test was protecting: an answer that is always in the document
    needs no keyboard handling, no announced expandable role and no JavaScript to read. So the
    assertion moved from "the accordion is native" to "there is no accordion", and the ten
    questions are still all there.
    """
    html = ABOUT.read_text(encoding="utf-8")
    assert html.count('<article class="qa__item"') == 10
    assert "<details" not in html and "<summary" not in html
    assert "aria-expanded" not in html
    # Nothing on the page may be hidden from a reader who has script turned off. This looks for
    # the `hidden` attribute itself rather than the substring, which would also match the
    # visually-hidden class that exists to expose things to screen readers, not to hide them.
    assert re.search(r"\shidden(?=[\s>])", html) is None


def test_no_text_on_the_site_carries_a_gradient():
    """The old world gave a gradient tint to exactly one phrase and this test counted it.

    Aurora has none. Colour lives in the light field and in the landing object, never in type, and
    gradient text is one of the clearest tells of generated work, so the rule inverted from "at
    most one" to "none at all". That is stricter than the rule it replaces, which is the only
    reason it is allowed to replace it.

    A gradient set in type is `background-clip: text`, prefixed or not, so counting the unprefixed
    property counts the rules regardless of prefixing.
    """
    css = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "assets" / "css").glob("*.css")))
    # Comments out first: a test that counts its own documentation passes for the wrong reason.
    declarations = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    tinted = re.findall(r"(?<!-)\bbackground-clip\s*:\s*text", declarations)
    assert tinted == [], f"gradient text is banned in this world, found {len(tinted)}"
