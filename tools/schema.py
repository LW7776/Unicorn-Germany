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
# The only codes the renderer can actually display. format_amount falls back to
# "<code> " for anything else, so an unknown code does not fail loudly — it prints
# "GBP 1bn" on the page and the crossing flag inherits it. Validated, not assumed.
KNOWN_CURRENCIES = frozenset(CURRENCY_SYMBOL)
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


def _trim_zeros(text):
    """Drop a trailing fractional zero run: "13.00" -> "13", "1.40" -> "1.4".

    The `"." in text` guard is load-bearing. On a string with no decimal point
    a bare rstrip("0") eats significant digits — "130" becomes "13" — which is
    a wrong figure, not a cosmetic one. Strings that still carry a point are
    safe on their own, because rstrip stops at the "." it cannot strip.
    """
    return text.rstrip("0").rstrip(".") if "." in text else text


def _plain_decimal(millions):
    """"102.5" for a fractional amount, "102" for a whole one — never "102.0".

    Formatting through "f" rather than "g" keeps large values out of scientific
    notation; the trailing "." left by rstrip("0") on a whole number is then
    removed, and the decimal point guards the significant zeros in "850".
    """
    return f"{millions:f}".rstrip("0").rstrip(".")


def _exact_billions(millions):
    """Millions expressed in billions with no rounding at all, trailing zeros
    dropped: 13000 -> "13", 1400 -> "1.4", 3250 -> "3.25", 1075 -> "1.075".

    This used to be f"{millions / 1000:.1f}", which had two faults at once.
    It rounded to one decimal, so a $3.25bn valuation printed as "$3.2 bn" —
    a figure no source stated, understating the company by $50m in the one
    place a reader looks. And `.1f` rounds half-to-even, so the direction of
    that error was not even predictable: 3.25 rounded down while 3.35 would
    round up. Decimal division from the string form keeps the value exact, so
    the label can only ever be the number that is on file.
    """
    return _trim_zeros(format(Decimal(str(millions)) / Decimal(1000), "f"))


def format_amount(millions, currency, approximate):
    """Render millions as a compact figure: 13000/USD -> "~$13 bn".

    No amount is ever rounded for display, at either scale. Sub-billion
    amounts keep any fractional part — a €102.5m round renders as "€102.5 m",
    not "€102 m" — and billion-scale amounts keep as many decimals as the
    value actually has, so 3250 renders "$3.25 bn" and 13000 still renders
    "$13 bn". Printing a figure the source never stated is the one thing this
    file exists to prevent.
    """
    symbol = CURRENCY_SYMBOL.get(currency, currency + " ")
    prefix = "~" if approximate else ""
    if millions >= 1000:
        return f"{prefix}{symbol}{_exact_billions(millions)} bn"
    return f"{prefix}{symbol}{_plain_decimal(millions)} m"


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
    """How a source might print this amount in billions, rounded as sources round.

    The unrounded form is generated alongside the rounded ones, and it is not
    redundant: quantising only to two and one places leaves a three-decimal
    figure unmatchable. A record of 1075 produced just {"1.08", "1.1"}, so a
    source that wrote "$1.075 billion" — the exact figure, and now exactly what
    format_amount prints for it — failed the quote check and the round could
    not be published at all. A figure the matcher cannot recognise is a figure
    the register cannot carry, so the renderer and the matcher have to agree on
    what the number looks like.
    """
    exact = Decimal(str(millions)) / Decimal(1000)
    forms = {_trim_zeros(format(exact, "f"))}
    for places in (2, 1):
        quantised = exact.quantize(Decimal("1." + "0" * places), rounding=ROUND_HALF_UP)
        forms.add(_trim_zeros(format(quantised, "f")))
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
        # Sub-billion rounds are routinely fractional — a €102.5m Series A, a
        # $27.5m seed. Sources print those with the decimal, English "102.5" or
        # German "102,5", so both forms are generated; without them such a round
        # has no expressible amount at all and a real, sourced round is silently
        # dropped from the record.
        #
        # The bare integer is only generated when it *is* the amount. Rounding a
        # fractional one to reach it (the old f"{millions:.0f}") yields a
        # different number, and inconsistently: 102.5 -> "102" but 27.5 -> "28".
        # That would let a quote saying "$28 million" satisfy a $27.5m record —
        # a false positive in the only check standing between this dataset and
        # an unsourced figure. For every whole amount this is byte-identical to
        # the previous behaviour.
        decimal = _plain_decimal(millions)
        forms.append((decimal, False))
        if "." in decimal:
            forms.append((decimal.replace(".", ","), False))
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
