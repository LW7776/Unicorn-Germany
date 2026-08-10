import { renderFooter } from "./footer.js";
import { revealWithin } from "./reveal.js";

/** Boot script for the static pages, about.html and impressum.html. These pages
    carry no register of their own, so they skip main.js entirely.

    Two of the About answers state numbers, and neither is typed into the page as
    fact. The twelve-month unicorn count and the register's size are read from
    data/companies.json, and the FX rate behind the combined headline is read from
    data/fx.json, both at runtime, so an answer can never drift from the data it
    describes. The markup carries the current values as its text, which is what a
    reader sees with JavaScript off and what the test in tests/test_pages.py pins
    against the data files. */
function fill(selector, value) {
  document.querySelectorAll(selector).forEach((node) => {
    node.textContent = value;
  });
}

async function loadJson(path) {
  const response = await fetch(path, { cache: "no-cache" });
  if (!response.ok) throw new Error(`${path} ${response.status}`);
  return response.json();
}

/** A deep link into one answer (about.html#data, which the register's freshness
    stat points at) has to open that row as well as scroll to it. A closed
    <details> has no height, so the browser's own fragment scrolling lands on the
    summary and the answer stays shut. */
function openLinkedRow() {
  const id = location.hash.slice(1);
  if (!id) return;
  const row = document.getElementById(id);
  if (row instanceof HTMLDetailsElement) {
    row.open = true;
    row.scrollIntoView();
  }
}

async function boot() {
  // First, and before any await. base.css holds every [data-reveal] block at
  // zero opacity, so the sooner this runs the sooner the page is guaranteed
  // readable — and there is nothing here it needs to wait for.
  revealWithin();

  renderFooter(document.querySelector("[data-footer]"));

  addEventListener("hashchange", openLinkedRow);
  openLinkedRow();

  // Only about.html carries these, so impressum.html fetches nothing.
  if (document.querySelector("[data-fx]")) {
    const fx = await loadJson("data/fx.json");
    fill('[data-fx="rate"]', fx.USD_EUR);
    fill('[data-fx="asof"]', fx.asOf);
  }
  if (document.querySelector("[data-stat]")) {
    const { stats } = await loadJson("data/companies.json");
    fill('[data-stat="new12"]', stats.newInLast12Months);
    fill('[data-stat="count"]', stats.count);
  }
}

boot().catch((error) => {
  // The authored fallbacks are already correct on the page, so a failure here
  // costs the reader nothing beyond a possibly stale number. The footer is the
  // one thing that renders empty, so it says so.
  console.error(error);
  revealWithin();
  const footer = document.querySelector("[data-footer]");
  if (footer && !footer.innerHTML.trim()) {
    footer.innerHTML =
      '<p>The footer could not be loaded. ' +
      '<a href="https://github.com/LW7776/Unicorn-Germany/issues/new" target="_blank" rel="noopener noreferrer">Report this on GitHub</a>.</p>';
  }
});
