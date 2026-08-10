/* The city window: click a city on the map, see the companies headquartered
   there, click one to open its entry.

   It is a second <dialog>, opened with showModal() over the map, and the company
   detail is a third opened over it. The browser's top layer stacks them, so each
   showModal() brings its own focus trap, its own backdrop and its own Escape
   handling, and none of that has to be re-implemented or coordinated here.

   The one rule that is not free: closing the detail window closes this one too. A
   reader who has just finished Moss's entry must not be dropped back onto a list
   of Berlin companies they are done with, so the pair collapses in one step and
   focus goes back to the city they clicked on the map. That is driven by
   detail.js's onDetailClose subscription rather than by watching its dialog's
   `close` event, because three of the four ways out of that window call
   closeDetail() directly and only Escape depends on the event.

   Every interpolated value comes from data/companies.json — pipeline output,
   untrusted like everywhere else — so it goes through escapeHtml() and every
   attribute stays quoted. */
import { escapeHtml } from "./html.js";
import { openDetail, onDetailClose } from "./detail.js";

let dialog;
let all = [];
// The companies listed in the window currently open, which is also the roster
// the ←/→ keys step through once a company is opened out of it.
let listed = [];
// Where focus goes once both windows are gone: the <g> for the city on the map,
// which is where the reader was standing.
let returnFocusTo = null;
// True while a company opened from this window is on screen, so detail.js's
// close signal can tell "the reader finished with a company they reached from
// here" from "a company opened from the grid, nothing to do with this window".
let detailIsOurs = false;
let settled = true;

function item(company) {
  return `
    <li>
      <button class="city__item" type="button" data-slug="${escapeHtml(company.slug)}">
        <span class="cell__plate city__plate">
          <img src="${escapeHtml(company.logo)}" alt="" loading="lazy" decoding="async">
        </span>
        <span class="city__name">${escapeHtml(company.name)}</span>
        <span class="city__figure">${escapeHtml(company.display.valuationLabel)}</span>
      </button>
    </li>`;
}

function markup(city, companies) {
  const count = companies.length;
  return `
    <button class="detail__close" type="button" data-close aria-label="Close">
      <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
        <path d="M3 3l10 10M13 3L3 13" stroke="currentColor" stroke-width="1.6" fill="none"/>
      </svg>
    </button>
    <header class="city__head">
      <p class="label">Headquarters</p>
      <h2>${escapeHtml(city)}</h2>
      <p class="city__meta">${count} ${count === 1 ? "company" : "companies"}</p>
    </header>
    <ul class="city__list">${companies.map(item).join("")}</ul>`;
}

/** Runs once per opening, whichever route out was taken. Idempotent for the same
    reason detail.js's afterClose is: the button path fires both the click handler
    and the native `close` event. */
function afterClose() {
  if (settled) return;
  settled = true;
  detailIsOurs = false;
  listed = [];
  // The detail window resets this too, but it may still be open above us if a
  // future caller ever closes this one first.
  if (!document.querySelector("[data-detail]")?.open) document.body.style.overflow = "";
  if (returnFocusTo?.isConnected) returnFocusTo.focus();
  returnFocusTo = null;
}

export function closeCityWindow() {
  if (dialog?.open) dialog.close();
  afterClose();
}

export function openCityWindow(city, { returnFocus = null } = {}) {
  listed = all.filter((company) => (company.hq?.city ?? "") === city);
  if (!listed.length) return;
  returnFocusTo = returnFocus;
  dialog.innerHTML = markup(city, listed);
  if (!dialog.open) dialog.showModal();
  document.body.style.overflow = "hidden";
  settled = false;
  dialog.querySelector("[data-close]").focus();
}

export function wireCityWindow(companies) {
  all = companies;
  dialog = document.querySelector("[data-city-window]");

  dialog.addEventListener("click", (event) => {
    if (event.target.closest("[data-close]") || event.target === dialog) {
      closeCityWindow();
      return;
    }
    const entry = event.target.closest(".city__item");
    if (!entry) return;
    const company = all.find((c) => c.slug === entry.dataset.slug);
    if (!company) return;
    detailIsOurs = true;
    // This city's companies become the roster the ←/→ keys step through, so
    // arrowing cannot wander out of the list the reader deliberately opened.
    // detail.js keeps the full register separately for every slug lookup.
    openDetail(company, { companies: listed });
  });

  // Escape and the backdrop go through the native close; the button path above
  // has already run afterClose(), which is why it guards itself.
  dialog.addEventListener("close", afterClose);

  // The double close.
  onDetailClose(() => {
    if (!detailIsOurs) return;
    closeCityWindow();
  });
}
