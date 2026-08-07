import { escapeHtml } from "./html.js";

/** Renders the footer shared by every page: the FX disclosure that backs the
    combined headline figure, and the Policy / About / Impressum / report-an-error
    links.

    Takes only the two fields it needs, `fxRateDisclosed` and `fxAsOf`, so it works
    identically whether the caller already has the full companies.json (index.html,
    via main.js's boot()) or fetched the much smaller data/fx.json directly (the
    static pages, which have no other reason to load the whole dataset). Both
    sources describe the same fixed rate: build.py copies fx.json's `USD_EUR`/`asOf`
    into companies.json's `stats.fxRateDisclosed`/`stats.fxAsOf` verbatim. */
export function renderFooter(container, { fxRateDisclosed, fxAsOf } = {}) {
  if (!container) return;
  const rate = escapeHtml(fxRateDisclosed);
  const asOf = escapeHtml(fxAsOf);
  container.innerHTML = `
    <p>Figures are indicative and carry the date they were reported.
       Combined value converts USD at ${rate} (${asOf}).</p>
    <nav aria-label="Footer">
      <a href="policy.html">Policy</a> · <a href="about.html">About</a> ·
      <a href="impressum.html">Impressum</a> ·
      <a href="https://github.com/LW7776/Unicorn-Germany/issues/new" target="_blank" rel="noopener noreferrer">Report an error</a>
    </nav>`;
}
