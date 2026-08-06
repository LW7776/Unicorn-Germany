import { Constellation } from "./constellation.js";
import { mountControls } from "./controls.js";
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

  const controls = mountControls({
    container: document.querySelector("[data-controls]"),
    companies: data.companies,
    onChange: (visible) => renderGrid(grid, visible),
  });
  window.__controls = controls;

  document.querySelector("[data-enter]").addEventListener("click", () => {
    enterRegister({
      hero: document.querySelector("[data-hero]"),
      register: document.querySelector("[data-register]"),
      sky, grid,
    }).catch((error) => {
      // The transition is decoration; the register is the product. If the
      // animation throws partway through, the viewer must still reach the
      // content rather than being stuck looking at whatever state the
      // failure left behind.
      console.error(error);
      document.querySelector("[data-register]").hidden = false;
      document.querySelector("[data-topbar]").hidden = false;
      document.querySelector("[data-hero]").hidden = true;
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
