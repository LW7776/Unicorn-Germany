/* The detail window. Content order is fixed by the spec; anything unknown renders "—".

   This renders the richest free text on the site — company names, thesis prose,
   founder names and roles, investor names, source titles and publications — all
   from data/companies.json, which is written by hand and by the update pipeline.
   Every interpolated value goes through escapeHtml(). escapeHtml() is safe inside
   element text and quoted attributes (every attribute below stays quoted) but NOT
   inside an unquoted one, and it does not make a URL safe — a source's `url` (and,
   defensively, a company's `website`) is only rendered as a link when its scheme
   is http: or https:; otherwise it renders as plain text. */
import { escapeHtml, isSafeUrl } from "./html.js";

// Dialog-switch and grid-entry animations are motion, not information — a
// viewer with reduced motion set should get the same content instantly, the
// same way transition.js and constellation.js already gate their animations.
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)");

let dialog, current, all = [];

const dash = (value) => (value === null || value === undefined || value === "" ? "—" : value);
/** Escape after applying the "—" fallback — safe for any scalar, including
    numbers and strings already containing HTML-significant characters. */
const text = (value) => escapeHtml(dash(value));

/** label and note are always literals at today's call sites, but escaping
    them here (rather than trusting every future caller to remember) means a
    call site that ever passes through data can't turn this into a footgun.
    `extra` is different: it is pre-built HTML (currently only disputedBadge's
    output) that already escaped everything it interpolated, so it is dropped
    in unescaped — treat it the same as note/label if a future call site ever
    wants to pass raw data through it. */
function figure(label, value, note, extra = "") {
  return `<div class="fig">
    <span class="label">${text(label)}</span>
    <span class="fig__value">${text(value)}</span>
    ${note ? `<span class="fig__note">${text(note)}</span>` : ""}
    ${extra}
  </div>`;
}

/** valuation.disputed: a conflicting figure recorded alongside the one on
    file (method.html — "Disputed"), rather than the site silently picking
    one on the reader's behalf. Renders a visible amber marker with the note
    and a link to the disputed figure's own source, exactly like any other
    cited claim — note is escaped and the source link goes through the same
    isSafeUrl gate as every other link on this page. */
function disputedBadge(disputed, sources) {
  if (!disputed) return "";
  const source = (sources || []).find((s) => s.id === disputed.source);
  const link = source ? sourceLink(source) : text(disputed.source);
  return `<span class="fig__disputed">
    <span class="fig__disputed-badge">disputed</span>
    <span class="fig__disputed-note">${text(disputed.note)}</span> — ${link}
  </span>`;
}

function timeline(company) {
  const unicornId = company.becameUnicorn.roundId;
  return `<ol class="timeline">${company.rounds.map((round, index) => `
    <li class="timeline__node ${round.id === unicornId ? "is-unicorn" : ""}"
        style="--i:${index}">
      <span class="timeline__dot" aria-hidden="true"></span>
      <span class="timeline__date">${text(round.dateLabel)}</span>
      <span class="timeline__stage">${text(round.stage)}</span>
      <span class="timeline__amount">${text(round.amountLabel)}</span>
      <span class="timeline__lead">${text((round.leadInvestors || []).join(", "))}</span>
      ${round.id === unicornId ? '<span class="timeline__flag">crossed €1bn</span>' : ""}
    </li>`).join("")}</ol>`;
}

/** A source's url is written by hand and by the update pipeline, so a scheme
    check runs before it is ever used as a link — escaping alone would not stop
    a `javascript:` URL from executing when clicked. */
function sourceLink(source) {
  const title = text(source.title);
  return isSafeUrl(source.url)
    ? `<a href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">${title}</a>`
    : `<span>${title}</span>`;
}

function sources(company) {
  return `<ol class="sources">${company.sources.map((source) => `
    <li>${sourceLink(source)}
      <span class="sources__meta">${text(source.publication)} · ${text(source.publishedOn)}</span></li>`).join("")}</ol>`;
}

function markup(company) {
  const d = company.display;
  const name = text(company.name);
  const logo = escapeHtml(company.logo);
  const slug = escapeHtml(company.slug);
  const websiteText = escapeHtml(company.website.replace("https://", ""));
  const site = isSafeUrl(company.website)
    ? `<a class="detail__site" href="${escapeHtml(company.website)}" target="_blank" rel="noopener noreferrer">${websiteText} ↗</a>`
    : `<span class="detail__site">${websiteText}</span>`;
  return `
  <button class="detail__close" type="button" data-close aria-label="Close">
    <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
      <path d="M3 3l10 10M13 3L3 13" stroke="currentColor" stroke-width="1.6" fill="none"/>
    </svg>
  </button>
  <header class="detail__head">
    <span class="cell__plate detail__plate"><img src="${logo}" alt="${name} logo"></span>
    <div>
      <h2>${name}</h2>
      <p class="detail__meta">
        ${text(company.hq.city)} · ${text((company.sectors || []).join(", "))} · Founded ${text(company.foundedYear)}
      </p>
      ${site}
    </div>
  </header>
  <div class="detail__figures">
    ${figure("Valuation", d.valuationLabel, `as of ${dash(d.valuationAsOf)}${d.aged ? " · aged" : ""}`,
      disputedBadge(company.valuation.disputed, company.sources))}
    ${figure("Last round", d.lastRoundStage, d.lastRoundLabel)}
    ${figure("Total raised", d.totalRaisedLabel)}
    ${figure("Years to €1bn", d.yearsToUnicorn, `unicorn ${dash(d.becameUnicornLabel)}`)}
  </div>
  <section class="detail__thesis">
    <div><h3 class="label">The problem</h3><p class="prose">${text(company.thesis.problem)}</p></div>
    <div><h3 class="label">Technology &amp; business model</h3><p class="prose">${text(company.thesis.solution)}</p></div>
  </section>
  <section><h3 class="label">Funding rounds</h3>${timeline(company)}</section>
  <section><h3 class="label">Investors</h3>
    <p class="detail__investors">${text((company.investorsOrdered || company.investors || []).join(" · "))}</p></section>
  <section><h3 class="label">Founders</h3>
    <p>${company.founders.length
      ? company.founders.map((f) => `${text(f.name)} <span class="detail__role">${text(f.role)}</span>`).join(" · ")
      : "—"}</p></section>
  <section><h3 class="label">Sources</h3>${sources(company)}</section>
  <footer class="detail__foot">
    <a href="https://github.com/LW7776/Unicorn-Germany/edit/main/data/companies/${slug}.json"
       target="_blank" rel="noopener noreferrer">Edit this entry ↗</a>
    <span>Committing there revalidates and rebuilds the site automatically.</span>
  </footer>`;
}

/** context.replace: true means "reuse the current history entry" — used for
    ←/→ navigation, where each step is a lateral move within one browsing
    session, not a new destination. Assigning location.hash always pushes a
    new entry, so left unchecked, flipping through companies with the arrow
    keys floods session history and the Back button starts stepping through
    companies one at a time instead of leaving the window. Grid clicks and
    deep links (context.replace left falsy) keep the normal pushing
    behaviour — that URL is meant to be shareable and back-navigable. */
export function openDetail(company, context = {}) {
  dialog = dialog || document.querySelector("[data-detail]");
  all = context.companies || all;
  current = company;
  dialog.innerHTML = markup(company);
  if (!dialog.open) dialog.showModal();
  document.body.style.overflow = "hidden";
  if (context.replace) {
    history.replaceState(null, "", `#/${company.slug}`);
  } else {
    location.hash = `#/${company.slug}`;
  }
  dialog.querySelector("[data-close]").focus();
  if (!REDUCED.matches) {
    dialog.animate({ opacity: [0, 1], transform: ["translateY(18px) scale(.985)", "none"] },
      { duration: 260, easing: "cubic-bezier(.22,1,.36,1)" });
  }
}

export function closeDetail() {
  if (dialog?.open) dialog.close();
  document.body.style.overflow = "";
  if (location.hash.startsWith("#/")) history.replaceState(null, "", location.pathname);
}

export function wireDetail(companies) {
  dialog = document.querySelector("[data-detail]");
  all = companies;

  dialog.addEventListener("click", (event) => {
    if (event.target.closest("[data-close]") || event.target === dialog) closeDetail();
  });
  // ESC triggers the browser's native dialog cancel/close, bypassing closeDetail()
  // entirely — this listener is the only thing that runs then, so it has to do
  // the full cleanup (not just the overflow reset) or ESC-closing leaves the
  // #/<slug> hash dangling and a reload would silently reopen the company.
  dialog.addEventListener("close", () => {
    document.body.style.overflow = "";
    if (location.hash.startsWith("#/")) history.replaceState(null, "", location.pathname);
  });
  dialog.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
    // Holding the key auto-repeats keydown; without this, each repeat would
    // still have opened a company (just onto a replaced history entry), so
    // holding ArrowRight would blow through the whole list in a blink.
    if (event.repeat) return;
    const index = all.findIndex((c) => c.slug === current.slug);
    const next = event.key === "ArrowRight" ? index + 1 : index - 1;
    if (all[next]) openDetail(all[next], { replace: true });
  });

  document.querySelector("[data-grid]").addEventListener("click", (event) => {
    const cell = event.target.closest(".cell");
    if (!cell) return;
    const company = all.find((c) => c.slug === cell.dataset.slug);
    if (company) openDetail(company, { companies: all });
  });

  const routeFromHash = () => {
    const slug = location.hash.replace("#/", "");
    if (!slug) return;
    const company = all.find((c) => c.slug === slug);
    if (company) {
      openDetail(company, { companies: all });
    } else if (dialog.open) {
      // The hash points at a slug that doesn't exist (bad deep link, edited
      // by hand, or a Back/Forward step landing on a stale entry) while a
      // company is still showing — closing keeps the address bar and the
      // visible window from silently disagreeing.
      closeDetail();
    }
  };
  addEventListener("hashchange", routeFromHash);
  if (location.hash.startsWith("#/")) routeFromHash();
}
