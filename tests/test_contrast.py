import pytest
from tools.check_contrast import contrast_ratio, SURFACES, TOKENS


def test_known_pair_matches_the_wcag_formula():
    assert contrast_ratio("#FFFFFF", "#000000") == pytest.approx(21.0, abs=0.01)


@pytest.mark.parametrize("token", ["--ink", "--muted", "--beam-text", "--amber", "--violet"])
@pytest.mark.parametrize("surface", list(SURFACES))
def test_every_text_token_clears_4_5_on_every_surface(token, surface):
    assert contrast_ratio(TOKENS[token], SURFACES[surface]) >= 4.5


def test_plate_ink_is_readable_on_the_logo_plate():
    assert contrast_ratio(TOKENS["--plate-ink"], TOKENS["--plate"]) >= 4.5


def test_the_dark_surface_inks_are_unreadable_on_the_plate():
    """Guards the trap: --ink on --plate is invisible, so --plate-ink must be used there."""
    assert contrast_ratio(TOKENS["--ink"], TOKENS["--plate"]) < 4.5
