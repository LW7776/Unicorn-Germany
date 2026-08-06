"""Asserts the palette clears WCAG AA. Run: python3 tools/check_contrast.py"""

TOKENS = {
    "--void": "#07080B",
    "--deep": "#0C0E14",
    "--ink": "#ECEEF3",
    "--muted": "#9AA1B1",
    "--beam": "#4C7DFF",
    "--beam-text": "#8FB0FF",
    "--violet": "#A97BFF",
    "--amber": "#E0A24B",
    "--plate": "#F7F8FA",
    "--plate-ink": "#14161A",
}
TEXT_TOKENS = ["--ink", "--muted", "--beam-text", "--amber", "--violet"]

PANEL_ALPHA = 0.045
PANEL_HOVER_ALPHA = 0.075


def _rgb(hex_colour):
    hex_colour = hex_colour.lstrip("#")
    return tuple(int(hex_colour[i:i + 2], 16) for i in (0, 2, 4))


def composite(foreground, background, alpha):
    """Flatten a translucent overlay onto an opaque background."""
    fg, bg = _rgb(foreground), _rgb(background)
    blended = tuple(round(alpha * f + (1 - alpha) * b) for f, b in zip(fg, bg))
    return "#%02X%02X%02X" % blended


SURFACES = {
    "--void": TOKENS["--void"],
    "--deep": TOKENS["--deep"],
    "--panel": composite("#FFFFFF", TOKENS["--deep"], PANEL_ALPHA),
    "--panel-hover": composite("#FFFFFF", TOKENS["--deep"], PANEL_HOVER_ALPHA),
}


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
            print(f"{token:>12} on {surface_name:<13}: {ratio:.2f}:1")
            if ratio < 4.5:
                failures.append(f"{token} on {surface_name} is {ratio:.2f}:1, below the 4.5:1 floor")

    plate_ratio = contrast_ratio(TOKENS["--plate-ink"], TOKENS["--plate"])
    print(f"{'--plate-ink':>12} on {'--plate':<13}: {plate_ratio:.2f}:1")
    if plate_ratio < 4.5:
        failures.append(f"--plate-ink on --plate is {plate_ratio:.2f}:1, below the 4.5:1 floor")

    for failure in failures:
        print("FAIL:", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
