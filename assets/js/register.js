import { escapeHtml, isSafeUrl } from "./html.js";

/** The threshold bar: this company's valuation against the largest on the
    register, with a tick where the qualifying billion sits.

    Both numbers are settled in tools/build.py (add_valuation_bars), so nothing
    here decides what a bar means — it only draws one. A company whose valuation
    no source has published gets no fill at all: an open-ended amber marker
    running right off the end of the track, because a bar of zero length would
    say "worth nothing" in the one place the register is trying hardest not to. */
function thresholdBar(company, thresholdPct) {
  const tick = thresholdPct === null || thresholdPct === undefined
    ? ""
    : `<span class="cell__tick" style="--at:${Number(thresholdPct)}%"></span>`;
  const pct = company.display.valuationBarPct;
  if (pct === null || pct === undefined) {
    return `<span class="cell__bar cell__bar--unknown" aria-hidden="true">${tick}</span>`;
  }
  return `<span class="cell__bar" aria-hidden="true">
    <span class="cell__fill" style="--fill:${Number(pct)}%"></span>${tick}</span>`;
}

/* Renders precomputed labels. No formatting logic lives in the browser. */
function cell(company, index, thresholdPct) {
  const aged = company.display.aged
    ? '<span class="cell__aged" title="The company has raised since this valuation was struck, or the figure is more than five years old">aged</span>'
    : "";
  // "Undisclosed" alone, in the slot where every other card prints a figure, would
  // read as "nothing is known" and — worse, next to "$8 bn" — as "worth nothing".
  // The amber marker beside it carries the one quantitative fact the register does
  // have: this company is over the threshold, and its unicorn status is sourced even
  // though its valuation is not. Same amber signal as `aged` and `disputed`: a
  // qualification on a figure, never an error.
  const undisclosed = company.display.valuationUndisclosed
    ? `<span class="cell__undisclosed" title="No source has published a figure. This company's unicorn status is itself sourced, so open the entry to read it.">${escapeHtml(company.display.valuationUndisclosedBadge)}</span>`
    : "";
  const name = escapeHtml(company.name);
  const slug = escapeHtml(company.slug);
  const logo = escapeHtml(company.logo);
  const valuationLabel = escapeHtml(company.display.valuationLabel);
  // The accessible name has to carry the qualification too — a screen reader reading
  // "Isar Aerospace, Undisclosed" off the card would be told strictly less than a
  // sighted reader, who can see the ">1bn" beside it.
  const spoken = company.display.valuationUndisclosed
    ? `valuation undisclosed, over 1 bn`
    : valuationLabel;
  // The card's own site, not the page that proves the figure. The evidence for
  // every number lives in the detail window, which is one click away and where a
  // reader who wants to check something is going anyway; the card is an index,
  // and the most useful onward link from an index is the company itself.
  // Same scheme gate as every other link built from this data.
  const site = isSafeUrl(company.website)
    ? `<a class="cell__site" href="${escapeHtml(company.website)}"
          target="_blank" rel="noopener noreferrer"
          aria-label="${name} website, opens in a new tab">${escapeHtml(company.display.websiteLabel)} ↗</a>`
    : "";
  // The crossing, still, and not the last funding round: the grid's default sort
  // is "Newest unicorn" (sort.newest, itself becameUnicorn.date — see
  // tools/build.py), so the date the card carries has to be the one the ordering
  // is keyed on. The year alone, though, because the row above now prints the
  // month the valuation was reported and two full dates on one card compete.
  // Sliced before escaping, never after — escaping first and cutting to four
  // characters would be one entity away from emitting half of one.
  const crossingYear = escapeHtml(String(company.display.becameUnicornLabel).slice(-4));
  const sectors = escapeHtml((company.sectors || [])[0] || "–");
  // The card is a <div> now rather than one big <button>, because the site link
  // has to be a real anchor and an anchor inside a button is invalid markup that
  // browsers resolve by dropping one of them. `.cell__open` is a transparent
  // button stretched over the whole card (register.css), so clicking anywhere
  // except the link still opens the entry, and Tab reaches the card and then the
  // link. detail.js keys its grid handler on .cell__open for the same reason:
  // that way the anchor is excluded by construction rather than by a guard
  // somebody has to remember.
  return `
    <div class="cell" role="listitem">
      <span class="cell__plate">
        <img src="${logo}" alt="${name} logo" loading="lazy" decoding="async">
      </span>
      <span class="cell__figure${company.display.valuationUndisclosed ? " cell__figure--undisclosed" : ""}">${valuationLabel}${undisclosed}${aged}</span>
      <span class="cell__rule" aria-hidden="true"></span>
      <span class="cell__meta">
        <span>${escapeHtml(company.display.valuationAsOf)}</span>${site}
      </span>
      ${thresholdBar(company, thresholdPct)}
      <span class="cell__foot">
        <span class="cell__sector">${sectors}</span>
        <span class="cell__year">${crossingYear}</span>
      </span>
      <button class="cell__open" type="button"
              data-slug="${slug}" data-index="${index}"
              aria-label="${name}, ${spoken}"></button>
    </div>`;
}

export function renderGrid(container, companies, thresholdPct = null) {
  container.innerHTML = companies.map((company, index) => cell(company, index, thresholdPct)).join("");
}

export function renderStats(container, stats) {
  // stats.dataAsOfLabel is settled in tools/build.py, like every other label on
  // this page, and is null when the dataset is empty (see build.py's
  // _data_as_of) — never a wall-clock value, and never assumed present.
  const freshness = escapeHtml(stats.dataAsOfLabel || "–");
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
    <a class="stat stat--freshness" href="about.html#data">
      <span class="stat__value">${freshness}</span>
      <span class="label">Data as of</span>
    </a>`;
}
