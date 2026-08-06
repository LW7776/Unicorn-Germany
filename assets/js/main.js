import { Constellation } from "./constellation.js";

async function loadData() {
  const response = await fetch("data/companies.json", { cache: "no-cache" });
  if (!response.ok) throw new Error(`companies.json ${response.status}`);
  return response.json();
}

export async function boot() {
  const data = await loadData();
  window.__data = data;

  document.querySelector('[data-stat="count"]').textContent = data.stats.count;

  const canvas = document.querySelector("[data-constellation]");
  const sky = new Constellation(canvas, data.companies.length);
  sky.start();
  window.__sky = sky;
}

boot().catch((error) => {
  console.error(error);
  document.querySelector("[data-hero]").insertAdjacentHTML(
    "beforeend",
    '<p class="hero__error" role="alert">The register could not be loaded. ' +
    'Reload the page, or report this on GitHub.</p>');
});
