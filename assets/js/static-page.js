import { renderFooter } from "./footer.js";

/** Boot script for the static pages (about.html, impressum.html). These pages
    carry no company data and never mount the register, so they skip main.js
    entirely. */
function boot() {
  renderFooter(document.querySelector("[data-footer]"));
}

boot();
