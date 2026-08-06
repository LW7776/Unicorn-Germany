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
}
TEXT_TOKENS = ["--ink", "--muted", "--beam-text", "--amber", "--violet"]


def _channel(value):
    value = value / 255
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def _luminance(hex_colour):
    hex_colour = hex_colour.lstrip("#")
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(a, b):
    la, lb = _luminance(a), _luminance(b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def main():
    failures = []
    for token in TEXT_TOKENS:
        ratio = contrast_ratio(TOKENS[token], TOKENS["--void"])
        print(f"{token:>12} on --void: {ratio:.2f}:1")
        if ratio < 4.5:
            failures.append(f"{token} is {ratio:.2f}:1, below the 4.5:1 floor")
    for failure in failures:
        print("FAIL:", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
