"""Field vocabulary shared by validate.py, build.py and watch.py.

All monetary amounts are millions of the stated currency: 13000 + "USD" is $13bn.
All dates are "YYYY" or "YYYY-MM" — never padded to a day the source did not give.
"""
import re
from decimal import Decimal, ROUND_HALF_UP

SOURCE_ALLOWLIST = {
    "Company press release", "Investor press release", "Handelsregister", "Bundesanzeiger",
    "Gründerszene", "Sifted", "EU-Startups", "Tech.eu", "TechCrunch",
    "Handelsblatt", "Reuters", "Bloomberg", "Financial Times",
}

CURRENCY_SYMBOL = {"EUR": "€", "USD": "$"}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

_DATE = re.compile(r"^(\d{4})(?:-(\d{2}))?$")
_FULL_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_date(value):
    """Return (year, month) for "YYYY-MM" or (year, 0) for "YYYY"."""
    match = _DATE.match(value or "")
    if not match:
        raise ValueError(f"date must be YYYY or YYYY-MM, got {value!r}")
    year, month_str = int(match.group(1)), match.group(2)
    month = int(month_str) if month_str else 0
    if month_str and (month < 1 or month > 12):
        raise ValueError(f"month out of range in {value!r}")
    return year, month


def is_full_date(value):
    return bool(_FULL_DATE.match(value or ""))


def date_sort_key(value):
    """Sortable across mixed precision. Year-only sorts before that year's months."""
    return parse_date(value)


def format_date(value):
    year, month = parse_date(value)
    return f"{MONTHS[month - 1]} {year}" if month else str(year)


def format_amount(millions, currency, approximate):
    """Render millions as a compact figure: 13000/USD -> "~$13 bn"."""
    symbol = CURRENCY_SYMBOL.get(currency, currency + " ")
    prefix = "~" if approximate else ""
    if millions >= 1000:
        billions = millions / 1000
        number = f"{billions:.1f}".rstrip("0").rstrip(".")
        return f"{prefix}{symbol}{number} bn"
    number = f"{millions:.0f}"
    return f"{prefix}{symbol}{number} m"


def figure_variants(millions):
    """String forms a source sentence might use for this amount.

    Used to prove a quote actually contains the figure it is cited for.
    """
    variants = {f"{millions:.0f}"}
    if millions >= 1000:
        billions = millions / 1000
        plain = f"{billions:.1f}".rstrip("0").rstrip(".")
        variants.add(plain)
        variants.add(plain.replace(".", ","))
        variants.add(f"{millions:,.0f}")           # 13,000
        variants.add(f"{millions:,.0f}".replace(",", "."))  # 13.000
    return variants


_SCALE_EN = r"(?:billions|billion|bn)(?![a-z])"
_SCALE_DE = r"(?:milliarden|milliarde|mrd\.?)(?![a-z])"
_CURRENCY_SYMBOLS = r"[$€]"
_CURRENCY_TOKENS = {
    "EUR": ("€", "eur", "euro"),
    "USD": ("$", "usd", "dollar"),
}


_UNICODE_SPACES = (" ", " ", " ", "　")


def _normalise_quote(quote):
    """Press releases and PDFs separate figures with non-breaking and thin spaces."""
    text = quote or ""
    for space in _UNICODE_SPACES:
        text = text.replace(space, " ")
    return text


def _billion_forms(millions):
    """How a source might print this amount in billions, rounded as sources round."""
    exact = Decimal(str(millions)) / Decimal(1000)
    forms = set()
    for places in (2, 1):
        quantised = exact.quantize(Decimal("1." + "0" * places), rounding=ROUND_HALF_UP)
        forms.add(format(quantised, "f").rstrip("0").rstrip("."))
    return forms


def _figure_forms(millions):
    """(form, needs_scale_word) pairs a source might use for this amount.

    Billion-scale forms need a scale word beside them: bare "1" must not match
    "1 March", but "1 billion" is a genuine statement of 1000 millions.
    """
    forms = []
    if millions >= 1000:
        for billions in _billion_forms(millions):
            forms.append((billions, True))
            forms.append((billions.replace(".", ","), True))
        forms.append((f"{millions:.0f}", False))
        forms.append((f"{millions:,.0f}", False))
        forms.append((f"{millions:,.0f}".replace(",", "."), False))
        forms.append((f"{millions:,.0f}".replace(",", " "), False))
    else:
        forms.append((f"{millions:.0f}", False))
    return forms


def quote_states_figure(quote, millions, currency=None):
    """True when the quote states this figure, with digit-boundary matching.

    Currency matching is presence-based: the quote must mention the currency
    somewhere. It cannot bind a currency to a specific number in prose, so it
    catches a mislabelled record, not a subtly wrong one.
    """
    text = _normalise_quote(quote).lower()
    if currency:
        tokens = _CURRENCY_TOKENS.get(currency)
        if tokens and not any(token in text for token in tokens):
            return False
    for form, needs_scale in _figure_forms(millions):
        escaped = re.escape(form)
        if needs_scale:
            patterns = (
                rf"(?<![\d.,]){escaped}[\s\-–—]*{_SCALE_EN}",
                rf"(?<![\d.,]){escaped}[\s\-–—]*{_SCALE_DE}",
                rf"{_CURRENCY_SYMBOLS}\s?{escaped}b(?![a-z0-9])",
            )
            if any(re.search(pattern, text) for pattern in patterns):
                return True
        else:
            pattern = rf"(?<![\d.,]){escaped}(?!\d)(?![.,]\d)"
            if re.search(pattern, text):
                return True
    return False
