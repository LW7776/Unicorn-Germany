import { Constellation } from "./constellation.js";
import { mountControls } from "./controls.js";
import { renderGrid, renderStats } from "./register.js";
import { enterRegister } from "./transition.js";
import { wireDetail } from "./detail.js";
import { openCityWindow, wireCityWindow } from "./city.js";
import { renderMap } from "./map.js";
import { renderFooter } from "./footer.js";
import { renderFunding, weekFromHash } from "./funding.js";

async function loadData() {
  const response = await fetch("data/companies.json", { cache: "no-cache" });
  if (!response.ok) throw new Error(`companies.json ${response.status}`);
  return response.json();
}

async function loadFunding() {
  const response = await fetch("data/funding.json", { cache: "no-cache" });
  if (!response.ok) throw new Error(`funding.json ${response.status}`);
  return response.json();
}

export async function boot() {
  const data = await loadData();
  window.__data = data;

  const canvas = document.querySelector("[data-constellation]");
  const sky = new Constellation(canvas, data.companies.length);
  sky.start();
  window.__sky = sky;

  const grid = document.querySelector("[data-grid]");
  renderGrid(grid, data.companies);
  renderStats(document.querySelector("[data-stats]"), data.stats);
  renderFooter(document.querySelector("[data-footer]"));

  const controls = mountControls({
    container: document.querySelector("[data-controls]"),
    companies: data.companies,
    onChange: (visible) => renderGrid(grid, visible),
  });
  window.__controls = controls;

  const mapEl = document.querySelector("[data-map]");
  const showView = async (view) => {
    const isMap = view === "map";
    document.querySelectorAll("[data-view]").forEach((button) =>
      button.setAttribute("aria-pressed", String(button.dataset.view === view)));
    grid.hidden = isMap;
    mapEl.hidden = !isMap;
    if (!isMap) return;
    try {
      // The map shows every company's headquarters, independent of the
      // grid's current search/sector/city filters — those apply to what
      // the grid lists, not to what the map summarises.
      await renderMap(mapEl, data.companies, {
        // A city is a place to look at companies, not a filter to apply to a
        // list somewhere else. Clicking one opens the city window over the
        // map; the company detail then opens over that, and closing the
        // detail takes both down (see assets/js/city.js).
        onSelectCity: (city, node) => openCityWindow(city, { returnFocus: node }),
      });
    } catch (error) {
      // data/geo/germany.json failing to fetch or parse must not leave
      // the map view blank with no explanation — the grid is still one
      // click away via the other [data-view] button.
      console.error(error);
      mapEl.innerHTML = '<p class="map__note">The map could not be loaded. Try the company list instead.</p>';
    }
  };
  document.querySelectorAll("[data-view]").forEach((button) => {
    button.addEventListener("click", () => showView(button.dataset.view));
  });
  // The topbar's Companies entry is an anchor to the register, but from the map
  // view "Companies" has to mean the list, not just a scroll position.
  document.querySelector("[data-companies-link]")?.addEventListener("click", () => showView("grid"));

  wireDetail(data.companies);
  wireCityWindow(data.companies);

  const roundup = document.querySelector("[data-roundup]");
  // The round-up is a second dataset with a second sourcing standard, so a
  // failure to load it must not take the register down with it — the register
  // is the product. Its own catch leaves the block explaining itself in place
  // of the weeks, rather than leaving a titled empty section on the page.
  try {
    const funding = await loadFunding();
    window.__funding = renderFunding(roundup, funding, data.companies);
  } catch (error) {
    console.error(error);
    roundup.innerHTML =
      '<div class="roundup__head"><p class="label">Weekly funding</p>' +
      '<h2 class="roundup__title">German rounds, week by week.</h2>' +
      '<p class="roundup__empty">The funding round-up could not be loaded. ' +
      'Reload the page, or <a href="https://github.com/LW7776/Unicorn-Germany/issues">report this on GitHub</a>.</p></div>';
  }

  const reveal = () => { roundup.hidden = false; };

  // A shared #funding link — the topbar's own entry, or #funding/2026-W30 for
  // one particular week — would otherwise land on a section still hidden
  // behind the hero. Enter the register straight away in that one case,
  // without the flight: the visitor asked for a specific place on the page,
  // not for the transition that leads to it.
  if (location.hash === "#funding" || weekFromHash(location.hash)) {
    document.querySelector("[data-hero]").hidden = true;
    document.querySelector("[data-register]").hidden = false;
    document.querySelector("[data-topbar]").hidden = false;
    sky.stop();
    reveal();
    roundup.scrollIntoView();
  }

  document.querySelector("[data-enter]").addEventListener("click", () => {
    reveal();
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
    'Reload the page, or <a href="https://github.com/LW7776/Unicorn-Germany/issues">report this on GitHub</a>.</p>');
});
