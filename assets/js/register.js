/* Renders precomputed labels. No formatting logic lives in the browser. */
function cell(company, index) {
  const aged = company.display.aged
    ? '<span class="cell__aged" title="This valuation is over two years old">aged</span>'
    : "";
  return `
    <button class="cell" role="listitem" type="button"
            data-slug="${company.slug}" data-index="${index}"
            aria-label="${company.name}, ${company.display.valuationLabel}">
      <span class="cell__plate">
        <img src="${company.logo}" alt="${company.name} logo" loading="lazy" decoding="async">
      </span>
      <span class="cell__figure">${company.display.valuationLabel}${aged}</span>
      <span class="cell__meta">Last round · ${company.display.lastRoundLabel}</span>
    </button>`;
}

export function renderGrid(container, companies) {
  container.innerHTML = companies.map(cell).join("");
}

export function renderStats(container, stats) {
  // stats.dataAsOf is a YYYY-MM-DD string, or null when the dataset is empty
  // (see tools/build.py:_data_as_of) — never a wall-clock value, and never
  // assumed present.
  const freshness = stats.dataAsOf ? stats.dataAsOf : "—";
  const items = [
    ["Unicorns", stats.count],
    ["Combined value", stats.combinedValuationLabel],
    ["New in 12 months", stats.newInLast12Months],
    ["Median years to €1bn", stats.medianYearsToUnicorn],
  ];
  container.innerHTML = items.map(([label, value]) => `
    <div class="stat">
      <span class="stat__value">${value}</span>
      <span class="label">${label}</span>
    </div>`).join("") + `
    <a class="stat stat--freshness" href="method.html">
      <span class="stat__value">Data as of ${freshness}</span>
      <span class="label">How this is verified</span>
    </a>`;
}
