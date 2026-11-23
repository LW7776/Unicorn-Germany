"""Asserts the palette clears WCAG AA. Run: python3 tools/check_contrast.py

This guards assets/css/aurora.css. It replaced a version that guarded the retired dark palette in
tokens.css, which was worse than useless for a while: it kept passing against colours no page used
any more, while a browser-based checker measured real text on the real page at 3.1:1. A gate that
validates a palette nothing renders is a gate that reports success for the wrong thing.

Every value below is copied from the `:root` block of assets/css/aurora.css. Change one there and
change it here, because this file is the only reason those values are allowed to be trusted.
"""

TOKENS = {
    # grounds
    "--bone": "#FAF8F4",
    "--bone-2": "#F3EFE8",
    "--card": "#FFFFFF",
    # ink
    "--ink": "#15130F",
    "--muted": "#544F46",
    "--faint": "#726C62",
    # the one accent allowed to be type
    "--action": "#2D3BC9",
    "--action-ink": "#FFFFFF",
    # the light field. These three are never set as type, which is why they are not in TEXT_TOKENS:
    # they live in the aurora and in the landing object and nowhere else.
    "--indigo": "#3D4EF5",
    "--rose": "#F2567E",
    "--amber": "#F2A33C",
}

# Text people actually read, plus the labels. --faint carries labels, dates and meta only, so it is
# held to the same 4.5:1 floor rather than to the stricter 7:1 the body copy is held to below.
TEXT_TOKENS = ["--ink", "--muted", "--faint", "--action"]

# Body copy is held higher than the AA floor: 7:1. --muted is the token that carries it, and the
# browser checker fails anything under 7:1 for running text, so the Python gate matches that rather
# than passing something the browser will reject.
BODY_TOKENS = ["--ink", "--muted"]
BODY_FLOOR = 7.0

SURFACES = {
    "--bone": TOKENS["--bone"],
    "--bone-2": TOKENS["--bone-2"],
    "--card": TOKENS["--card"],
}

# ---------------------------------------------------------------------------
# The landing is the one place on this site where text sits over the light field rather than over a
# flat surface, and for a while it was failing badly while this file reported a pass: measured on
# the rendered page, the stat labels came out at 1.51:1 and the figures at 5.93:1. Nothing here saw
# it, because every check in this file compares a token against bone, and bone was not what was
# behind the text. That is the same mistake the docstring describes, one layer up.
#
# It is not fixable here. Whether the landing passes depends on where the text actually ends inside
# a blurred, animated gradient, which is a question about the rendered page and not about a palette.
# Modelling it in Python meant inventing an alpha, and the invented number failed a page that
# measures clean. So the landing has its own gate instead, in a real browser:
#
#     node tools/check_landing_contrast.mjs
#
# It samples every text element on the landing against the ground actually behind its glyphs, at
# both viewports. Run it after touching the aurora, the veil, or anything in the landing's copy.
# test_contrast.py asserts the veil exists so it cannot be quietly deleted between runs.


def _rgb(hex_colour):
    hex_colour = hex_colour.lstrip("#")
    return tuple(int(hex_colour[i:i + 2], 16) for i in (0, 2, 4))


def composite(foreground, background, alpha):
    """Flatten a translucent overlay onto an opaque background."""
    fg, bg = _rgb(foreground), _rgb(background)
    blended = tuple(round(alpha * f + (1 - alpha) * b) for f, b in zip(fg, bg))
    return "#%02X%02X%02X" % blended


def _channel(value):
    value = value / 255
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def _luminance(hex_colour):
    r, g, b = _rgb(hex_colour)
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(a, b):
    la, lb = _luminance(a), _luminance(b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def main():
    failures = []

    for token in TEXT_TOKENS:
        for surface_name, surface_hex in SURFACES.items():
            ratio = contrast_ratio(TOKENS[token], surface_hex)
            print(f"{token:>13} on {surface_name:<10}: {ratio:5.2f}:1")
            if ratio < 4.5:
                failures.append(f"{token} on {surface_name} is {ratio:.2f}:1, below the 4.5:1 floor")

    print()
    for token in BODY_TOKENS:
        for surface_name, surface_hex in SURFACES.items():
            ratio = contrast_ratio(TOKENS[token], surface_hex)
            if ratio < BODY_FLOOR:
                failures.append(
                    f"{token} on {surface_name} is {ratio:.2f}:1, below the {BODY_FLOOR}:1 floor "
                    f"for running text")
    print(f"body copy floor {BODY_FLOOR}:1 checked for {', '.join(BODY_TOKENS)}")

    print()
    print("landing: measured separately in a browser, see tools/check_landing_contrast.mjs")

    # A filled button's label against its own ground.
    pairs = [("--action-ink", "--action"), ("--bone", "--ink")]
    for ink, ground in pairs:
        ratio = contrast_ratio(TOKENS[ink], TOKENS[ground])
        print(f"{ink:>13} on {ground:<10}: {ratio:5.2f}:1")
        if ratio < 4.5:
            failures.append(f"{ink} on {ground} is {ratio:.2f}:1, below the 4.5:1 floor")

    for failure in failures:
        print("FAIL:", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
