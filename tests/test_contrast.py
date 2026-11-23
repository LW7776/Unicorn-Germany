import pathlib

import pytest
from tools.check_contrast import (
    BODY_FLOOR,
    BODY_TOKENS,
    SURFACES,
    TEXT_TOKENS,
    TOKENS,
    contrast_ratio,
)


def test_known_pair_matches_the_wcag_formula():
    assert contrast_ratio("#FFFFFF", "#000000") == pytest.approx(21.0, abs=0.01)


@pytest.mark.parametrize("token", TEXT_TOKENS)
@pytest.mark.parametrize("surface", list(SURFACES))
def test_every_text_token_clears_4_5_on_every_surface(token, surface):
    assert contrast_ratio(TOKENS[token], SURFACES[surface]) >= 4.5


@pytest.mark.parametrize("token", BODY_TOKENS)
@pytest.mark.parametrize("surface", list(SURFACES))
def test_running_text_clears_the_stricter_body_floor(token, surface):
    """Body copy is held to 7:1, not to the 4.5:1 AA floor.

    The browser-based checker fails running text under 7:1, and a Python gate that stopped at 4.5
    would hand back a pass for something the browser then rejects. The two agree deliberately.
    """
    assert contrast_ratio(TOKENS[token], SURFACES[surface]) >= BODY_FLOOR


def test_a_filled_button_label_is_readable_on_its_own_ground():
    assert contrast_ratio(TOKENS["--action-ink"], TOKENS["--action"]) >= 4.5
    assert contrast_ratio(TOKENS["--bone"], TOKENS["--ink"]) >= 4.5


@pytest.mark.parametrize("token", ["--indigo", "--rose", "--amber"])
def test_the_light_field_colours_are_never_in_the_text_set(token):
    """Guards the rule rather than the ratio.

    Indigo, rose and amber live in the aurora and in the landing object, and nowhere else. The rule
    is their absence from TEXT_TOKENS, so that absence is what gets asserted.
    """
    assert token not in TEXT_TOKENS


@pytest.mark.parametrize("token", ["--rose", "--amber"])
def test_rose_and_amber_could_never_be_promoted_to_text(token):
    """These two fail the floor outright, so the rule above is also enforced by the numbers."""
    assert contrast_ratio(TOKENS[token], TOKENS["--bone"]) < 4.5


def test_indigo_is_readable_but_still_not_the_text_accent():
    """Indigo clears 4.5:1 on bone at about 5.5, which is exactly the trap.

    It is readable enough to look fine in a heading and not readable enough for the 7:1 body floor,
    so a later edit could reach for it and ship something that passes AA and fails this project's
    own bar. --action is the darkened indigo that exists for that job, and this records why.
    """
    assert contrast_ratio(TOKENS["--indigo"], TOKENS["--bone"]) >= 4.5
    assert contrast_ratio(TOKENS["--indigo"], TOKENS["--bone"]) < BODY_FLOOR
    assert contrast_ratio(TOKENS["--action"], TOKENS["--bone"]) >= BODY_FLOOR


def test_the_faint_token_is_not_allowed_to_carry_running_text():
    """--faint clears 4.5:1 for labels and dates but not the 7:1 body floor, which is the point.

    It exists so metadata can sit back from the copy. If it ever cleared 7:1 it would stop being a
    quieter level and the hierarchy it was introduced for would collapse.
    """
    assert contrast_ratio(TOKENS["--faint"], TOKENS["--bone"]) >= 4.5
    assert contrast_ratio(TOKENS["--faint"], TOKENS["--bone"]) < BODY_FLOOR


def test_the_landing_lays_a_veil_between_the_light_field_and_the_words():
    """The landing is the one surface where the palette gate cannot answer the question.

    Text there sits over the aurora, so what is behind a word depends on a blurred animated
    gradient rather than on a token. The landing shipped once with its stat labels at 1.51:1 while
    check_contrast.py reported a clean pass, because that file compares tokens against bone and
    bone was not what was behind the text.

    The veil is what fixed it, and it is load-bearing rather than decorative. This asserts it is
    still there at both layouts, so it cannot be deleted silently. Whether it is still doing its
    job is a question for the browser: playwright-cli run-code --filename=tools/check_landing_contrast.js
    """
    css = pathlib.Path("assets/css/aurora.css").read_text()
    veil = css.split(".landing::before")
    assert len(veil) >= 3, "the landing veil is missing a layout: there should be a wide and a narrow one"
    for block in veil[1:]:
        body = block[: block.index("}")]
        assert "linear-gradient" in body, "the veil must be a gradient over the field"
        assert "250, 248, 244" in body or "var(--bone)" in body, "the veil must be made of bone"


def test_the_aurora_is_never_set_directly_behind_body_copy_without_that_veil():
    """Guards the rule rather than a ratio, because the ratio lives in the browser.

    If a later edit gives another element the aurora as its own background, that element's text has
    no veil and nothing in Python would notice.
    """
    css = pathlib.Path("assets/css/aurora.css").read_text()
    aurora_rules = [b for b in css.split("}") if "radial-gradient" in b and "--indigo" in b]
    assert len(aurora_rules) == 1, (
        "the aurora field is declared in more than one place, so the veil may not cover all of it")
    assert ".aurora" in aurora_rules[0], "the aurora field must stay on .aurora"
