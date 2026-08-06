"""Field vocabulary shared by validate.py, build.py and watch.py.

All monetary amounts are millions of the stated currency: 13000 + "USD" is $13bn.
All dates are "YYYY" or "YYYY-MM" — never padded to a day the source did not give.
"""
import re

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
