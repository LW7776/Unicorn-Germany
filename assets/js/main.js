import { Constellation } from "./constellation.js";
import { renderGrid, renderStats } from "./register.js";
import { enterRegister } from "./transition.js";

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

  const grid = document.querySelector("[data-grid]");
  renderGrid(grid, data.companies);
  renderStats(document.querySelector("[data-stats]"), data.stats);

  document.querySelector("[data-enter]").addEventListener("click", () => {
    enterRegister({
      hero: document.querySelector("[data-hero]"),
      register: document.querySelector("[data-register]"),
      sky, grid,
    });
  });
}

boot().catch((error) => {
  console.error(error);
  document.querySelector("[data-hero]").insertAdjacentHTML(
    "beforeend",
    '<p class="hero__error" role="alert">The register could not be loaded. ' +
    'Reload the page, or <a href="https://github.com/OWNER/REPO/issues">report this on GitHub</a>.</p>');
});
