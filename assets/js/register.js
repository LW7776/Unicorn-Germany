import { escapeHtml } from "./html.js";

/* Renders precomputed labels. No formatting logic lives in the browser. */
function cell(company, index) {
  const aged = company.display.aged
    ? '<span class="cell__aged" title="This valuation is over two years old">aged</span>'
    : "";
  const name = escapeHtml(company.name);
  const slug = escapeHtml(company.slug);
  const logo = escapeHtml(company.logo);
  const valuationLabel = escapeHtml(company.display.valuationLabel);
  const lastRoundLabel = escapeHtml(company.display.lastRoundLabel);
  return `
    <button class="cell" role="listitem" type="button"
            data-slug="${slug}" data-index="${index}"
            aria-label="${name}, ${valuationLabel}">
      <span class="cell__plate">
        <img src="${logo}" alt="${name} logo" loading="lazy" decoding="async">
      </span>
      <span class="cell__figure">${valuationLabel}${aged}</span>
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
    ["Combined value", stats.combinedValuationLabel],
    ["New in 12 months", stats.newInLast12Months],
    ["Median years to €1bn", stats.medianYearsToUnicorn],
  ];
  container.innerHTML = items.map(([label, value]) => `
    <div class="stat">
      <span class="stat__value">${escapeHtml(value)}</span>
      <span class="label">${label}</span>
    </div>`).join("") + `
    <a class="stat stat--freshness" href="method.html">
      <span class="stat__value">Data as of ${freshness}</span>
      <span class="label">How this is verified</span>
    </a>`;
}
