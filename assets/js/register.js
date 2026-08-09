import { escapeHtml } from "./html.js";

/* Renders precomputed labels. No formatting logic lives in the browser. */
function cell(company, index) {
  const aged = company.display.aged
    ? '<span class="cell__aged" title="This valuation is over two years old">aged</span>'
    : "";
  // "Undisclosed" alone, in the slot where every other card prints a figure, would
  // read as "nothing is known" and — worse, next to "$8 bn" — as "worth nothing".
  // The amber marker beside it carries the one quantitative fact the register does
  // have: this company is over the threshold, and its unicorn status is sourced even
  // though its valuation is not. Same amber signal as `aged` and `disputed`: a
  // qualification on a figure, never an error.
  const undisclosed = company.display.valuationUndisclosed
    ? `<span class="cell__undisclosed" title="No source has published a figure — this company's unicorn status is itself sourced. Open the entry to read it.">${escapeHtml(company.display.valuationUndisclosedBadge)}</span>`
    : "";
  const name = escapeHtml(company.name);
  const slug = escapeHtml(company.slug);
  const logo = escapeHtml(company.logo);
  const valuationLabel = escapeHtml(company.display.valuationLabel);
  const lastRoundLabel = escapeHtml(company.display.lastRoundLabel);
  // The accessible name has to carry the qualification too — a screen reader reading
  // "Isar Aerospace, Undisclosed" off the card would be told strictly less than a
  // sighted reader, who can see the ">1bn" beside it.
  const spoken = company.display.valuationUndisclosed
    ? `valuation undisclosed, over 1 bn`
    : valuationLabel;
  return `
    <button class="cell" role="listitem" type="button"
            data-slug="${slug}" data-index="${index}"
            aria-label="${name}, ${spoken}">
      <span class="cell__plate">
        <img src="${logo}" alt="${name} logo" loading="lazy" decoding="async">
      </span>
      <span class="cell__figure${company.display.valuationUndisclosed ? " cell__figure--undisclosed" : ""}">${valuationLabel}${undisclosed}${aged}</span>
      <span class="cell__meta">Last round · ${lastRoundLabel}</span>
    </button>`;
}

export function renderGrid(container, companies) {
  container.innerHTML = companies.map(cell).join("");
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** "2026-07-18" -> "Jul 2026". Month precision matches how every other date renders. */
function asOfLabel(dataAsOf) {
  if (!dataAsOf) return "—";
  const [year, month] = dataAsOf.split("-");
  return `${MONTHS[Number(month) - 1]} ${year}`;
}

export function renderStats(container, stats) {
  // stats.dataAsOf is a YYYY-MM-DD string, or null when the dataset is empty
  // (see tools/build.py:_data_as_of) — never a wall-clock value, and never
  // assumed present.
  const freshness = escapeHtml(asOfLabel(stats.dataAsOf));
  const items = [
    ["Unicorns", stats.count],
    // Not a fixed string: companies whose valuation no source has published are left
    // out of the sum rather than counted as zero, and when any are, the caption says
    // how many of the register the figure covers (tools/build.py: combinedValuationBasis).
    [stats.combinedValuationBasis || "Combined value", stats.combinedValuationLabel],
    ["New in 12 months", stats.newInLast12Months],
    // Not "to €1bn": this median runs across a register where most companies
    // crossed the dollar threshold, not the euro one (the rule is "$1B **or**
    // €1B, as reported"). Naming one currency for an aggregate spanning both
    // states a fact about the set that is not true of most of its members —
    // the same defect the per-round flag had. Each detail page still names the
    // threshold its own crossing round actually cleared.
    ["Median years to unicorn", stats.medianYearsToUnicorn],
  ];
  container.innerHTML = items.map(([label, value]) => `
    <div class="stat">
      <span class="stat__value">${escapeHtml(value)}</span>
      <span class="label">${label}</span>
    </div>`).join("") + `
    <a class="stat stat--freshness" href="about.html#built">
      <span class="stat__value">Data as of ${freshness}</span>
      <span class="label">How this is verified</span>
    </a>`;
}
