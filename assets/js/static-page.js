import { renderFooter } from "./footer.js";

/** Boot script for the static pages (method.html, about.html, impressum.html).
    These pages carry no company data and never mount the register, so they skip
    main.js entirely; the only thing they need at runtime is the FX rate that the
    Method page and the footer both disclose, read straight from data/fx.json
    rather than hard-coded, so it can never drift from the value build.py bakes
    into companies.json. */
async function loadFx() {
  const response = await fetch("data/fx.json", { cache: "no-cache" });
  if (!response.ok) throw new Error(`fx.json ${response.status}`);
  return response.json();
}

async function boot() {
  const fx = await loadFx();

  renderFooter(document.querySelector("[data-footer]"), {
    fxRateDisclosed: fx.USD_EUR,
    fxAsOf: fx.asOf,
  });

  // Only method.html carries these; harmless no-ops elsewhere.
  const rate = document.querySelector("[data-fx-rate]");
  const asOf = document.querySelector("[data-fx-asof]");
  if (rate) rate.textContent = fx.USD_EUR;
  if (asOf) asOf.textContent = fx.asOf;
}

boot().catch((error) => {
  console.error(error);
  const footer = document.querySelector("[data-footer]");
  if (footer) {
    footer.innerHTML =
      '<p>The footer could not be loaded. ' +
      '<a href="https://github.com/LW7776/Unicorn-Germany/issues/new" target="_blank" rel="noopener noreferrer">Report this on GitHub</a>.</p>';
  }
});
