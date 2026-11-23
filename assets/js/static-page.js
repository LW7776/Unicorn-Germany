// Boot script for the static pages, about.html and impressum.html.
//
// These pages carry no register of their own. Two of the About answers state numbers, and neither
// is typed into the page as fact: the twelve-month count and the register's size are read from
// data/companies.json, and the FX rate behind the combined headline from data/fx.json, both at
// runtime, so an answer can never drift from the data it describes. The markup carries the current
// values as its text, which is what a reader sees with JavaScript off and what the test in
// tests/test_pages.py pins against the data files.

import { revealSections, wireProgress } from "./charts.js";

function fill(selector, value) {
  document.querySelectorAll(selector).forEach((node) => { node.textContent = value; });
}

async function loadJson(path) {
  const response = await fetch(path, { cache: "no-cache" });
  if (!response.ok) throw new Error(`${path} ${response.status}`);
  return response.json();
}

async function boot() {
  wireProgress();
  revealSections();
  try {
    const [data, fx] = await Promise.all([
      loadJson("data/companies.json"),
      loadJson("data/fx.json").catch(() => null),
    ]);
    const stats = data.stats || {};
    fill('[data-stat="count"]', stats.count);
    fill('[data-stat="new12"]', stats.newInLast12Months);
    if (fx) {
      fill('[data-fx="rate"]', fx.USD_EUR);
      fill('[data-fx="asof"]', fx.asOf);
    }
  } catch (error) {
    // The authored values are already correct in the markup, so a failed fetch leaves the page
    // reading exactly as it would have. There is nothing to recover and nothing to apologise for.
    console.error(error);
  }
}

boot();
