import pytest
from tools.check_contrast import contrast_ratio, TOKENS


def test_known_pair_matches_the_wcag_formula():
    assert contrast_ratio("#FFFFFF", "#000000") == pytest.approx(21.0, abs=0.01)


@pytest.mark.parametrize("token", ["--ink", "--muted", "--beam-text", "--amber", "--violet"])
def test_every_text_token_clears_4_5_on_the_page_background(token):
    assert contrast_ratio(TOKENS[token], TOKENS["--void"]) >= 4.5
