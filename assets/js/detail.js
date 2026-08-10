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

// `all` is the whole register and is set once, by wireDetail. `roster` is the
// list the ←/→ keys step through, which is not always the same thing: a company
// opened from the city window steps through that city's companies. Keeping them
// apart matters because every slug lookup below (grid clicks, deep links) has to
// search the full register — when these were one variable, opening a company
// from a narrowed list quietly narrowed the lookup table too, and the next grid
// click on anything outside that list found nothing.
let dialog, current, all = [], roster = [];

// Cleanup after the window is gone runs exactly once per opening, whichever of
// the four routes out was taken: the close button, the backdrop, Escape (which
// fires the native `close` event and never reaches closeDetail) or a
// programmatic close. `settled` is what makes "exactly once" true when two of
// those fire in sequence, as the button path does.
let settled = true;
const closeListeners = new Set();

/** Subscribe to "the company window has gone away". city.js uses this to take
    its own window down with it, and it deliberately does not sit on the `close`
    event alone: three of the four routes out go through closeDetail(), so a
    subscriber keeps working even where a browser is stingy about firing
    `close`. */
export function onDetailClose(listener) {
  closeListeners.add(listener);
}

function afterClose() {
  if (settled) return;
  settled = true;
  document.body.style.overflow = "";
  // ESC-closing must not leave the #/<slug> hash dangling, or a reload would
  // silently reopen the company the reader just dismissed.
  if (location.hash.startsWith("#/")) history.replaceState(null, "", location.pathname);
  closeListeners.forEach((listener) => listener());
}

const dash = (value) => (value === null || value === undefined || value === "" ? "–" : value);
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
function figure(label, value, note, extra = "", valueClass = "") {
  return `<div class="fig">
    <span class="label">${text(label)}</span>
    <span class="fig__value${valueClass ? " " + valueClass : ""}">${text(value)}</span>
    ${note ? `<span class="fig__note">${text(note)}</span>` : ""}
    ${extra}
  </div>`;
}

/** A conflicting figure recorded alongside the one on file, flagged "Disputed",
    rather than the site silently picking one on the reader's behalf. Used both
    on `valuation` and on a round whose amount the sources disagree about — a
    reader must be able to see the disagreement without opening every source.
    Renders a visible amber marker with the note
    and a link to the disputed figure's own source, exactly like any other
    cited claim — note is escaped and the source link goes through the same
    isSafeUrl gate as every other link on this page. */
function disputedBadge(disputed, sources) {
  if (!disputed) return "";
  const source = (sources || []).find((s) => s.id === disputed.source);
  const link = source ? sourceLink(source) : text(disputed.source);
  return `<span class="fig__disputed">
    <span class="fig__disputed-badge">disputed</span>
    <span class="fig__disputed-note">${text(disputed.note)}</span> · ${link}
  </span>`;
}

/** The other half of `disputed`: evidence that a company (or a crossing round) is over
    the threshold where no allowlisted source ever printed a figure. Shaped and
    source-checked identically by tools/validate.py, and rendered in the same amber
    signal — a qualification on a figure, not an error, and never an absence. It appears
    on `valuation`, and on the crossing round whose post-money nobody disclosed. */
function undisclosedBadge(undisclosed, sources, label = "valuation undisclosed") {
  if (!undisclosed) return "";
  const source = (sources || []).find((s) => s.id === undisclosed.source);
  const link = source ? sourceLink(source) : text(undisclosed.source);
  return `<span class="fig__disputed fig__undisclosed">
    <span class="fig__disputed-badge">${text(label)}</span>
    <span class="fig__disputed-note">${text(undisclosed.note)}</span> · ${link}
  </span>`;
}

function timeline(company) {
  const unicornId = company.becameUnicorn.roundId;
  // "crossed $1bn" / "crossed €1bn" — settled in tools/build.py from the crossing
  // round's own post-money currency, because the inclusion rule is "$1B or €1B, as
  // reported" and a company that crossed at "$1.1 billion" did not cross €1bn. When
  // that round disclosed no price at all, the same function says "reached unicorn
  // status" instead, rather than naming a threshold off the currency of the money
  // raised — which is a different number in a different sentence.
  const crossingFlag = text(company.display.unicornFlagLabel);
  return `<ol class="timeline">${company.rounds.map((round, index) => `
    <li class="timeline__node ${round.id === unicornId ? "is-unicorn" : ""}"
        style="--i:${index}">
      <span class="timeline__dot" aria-hidden="true"></span>
      <span class="timeline__date">${text(round.dateLabel)}</span>
      <span class="timeline__stage">${text(round.stage)}</span>
      <span class="timeline__amount">${text(round.amountLabel)}</span>
      <span class="timeline__lead">${text((round.leadInvestors || []).join(", "))}</span>
      ${round.id === unicornId ? `<span class="timeline__flag">${crossingFlag}</span>` : ""}
      ${/* On a round the undisclosed thing is the price of the round, not the
            company's headline valuation — say which. */""}
      ${undisclosedBadge(round.undisclosed, company.sources, "post-money undisclosed")}
      ${disputedBadge(round.disputed, company.sources)}
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
      <span class="sources__meta">${text(source.publication)} · ${text(source.publishedLabel)}</span></li>`).join("")}</ol>`;
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
  // Dual-HQ companies (Celonis is Munich and New York, for example) carry
  // an explicit alsoBasedIn list; render it right after the HQ city so a
  // second headquarters is never dropped from the one place HQ is shown.
  const alsoBasedIn = (company.alsoBasedIn || []).length
    ? ` · also ${text(company.alsoBasedIn.join(", "))}`
    : "";
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
        ${text(company.hq.city)}${alsoBasedIn} · ${
          // `sectors` now holds the broad industry (or industries) that also drive
          // the grid's filter chips — deliberately coarse. `niche` is the specific
          // descriptor that would make a near-useless filter chip ("Process
          // Mining", "Spend Management") but is exactly the detail a reader wants
          // once they have opened one company, so it still appears here, right
          // beside the broad category rather than replacing it.
          text([...(company.sectors || []), company.niche].filter(Boolean).join(", "))
        } · Founded ${text(company.foundedYear)}
      </p>
      ${site}
    </div>
  </header>
  <div class="detail__figures">
    ${figure("Valuation", d.valuationLabel,
      d.valuationUndisclosed
        // "as of" a date, on a value that is not a figure, would read as though a
        // figure had been struck then. What that date marks is when the evidence was
        // published — say so, and keep the staleness flag it still drives.
        ? `${dash(d.valuationUndisclosedBadge)} · reported ${dash(d.valuationAsOf)}${d.aged ? " · aged" : ""}`
        : `as of ${dash(d.valuationAsOf)}${d.aged ? " · aged" : ""}`,
      undisclosedBadge(company.valuation.undisclosed, company.sources)
      + disputedBadge(company.valuation.disputed, company.sources),
      // "Undisclosed" is a word, not a figure: eleven characters where the other
      // tiles hold four or five ("$8 bn"). At the figure size it overruns a
      // 11rem grid column and spills into the tile beside it, so it is set one
      // step down — still the largest thing in its own tile, and it fits.
      d.valuationUndisclosed ? "fig__value--undisclosed" : "")}
    ${figure("Last round", d.lastRoundStage, d.lastRoundLabel)}
    ${figure(`Years to ${text(d.unicornThresholdLabel)}`, d.yearsToUnicorn, `unicorn ${dash(d.becameUnicornLabel)}`)}
  </div>
  <section class="detail__thesis">
    <div><h3 class="label">Problem</h3><p class="prose">${text(company.thesis.problem)}</p></div>
    <div><h3 class="label">Technology and business model</h3><p class="prose">${text(company.thesis.solution)}</p></div>
  </section>
  <section><h3 class="label">Funding rounds</h3>${timeline(company)}</section>
  <section><h3 class="label">Investors</h3>
    <p class="detail__investors">${text((company.investorsOrdered || company.investors || []).join(" · "))}</p></section>
  <section><h3 class="label">Founders</h3>
    <p>${company.founders.length
      ? company.founders.map((f) => `${text(f.name)} <span class="detail__role">${text(f.role)}</span>`).join(" · ")
      : "–"}</p></section>
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
  // A lateral ←/→ step keeps the roster it is stepping through; anything else
  // sets a new one, defaulting to the whole register.
  if (!context.replace) roster = context.companies || all;
  current = company;
  dialog.innerHTML = markup(company);
  if (!dialog.open) dialog.showModal();
  document.body.style.overflow = "hidden";
  if (context.replace) {
    history.replaceState(null, "", `#/${company.slug}`);
  } else {
    location.hash = `#/${company.slug}`;
  }
  settled = false;
  dialog.querySelector("[data-close]").focus();
  if (!REDUCED.matches) {
    dialog.animate({ opacity: [0, 1], transform: ["translateY(18px) scale(.985)", "none"] },
      { duration: 260, easing: "cubic-bezier(.22,1,.36,1)" });
  }
}

export function closeDetail() {
  if (dialog?.open) dialog.close();
  afterClose();
}

export function wireDetail(companies) {
  dialog = document.querySelector("[data-detail]");
  all = companies;
  roster = companies;

  dialog.addEventListener("click", (event) => {
    if (event.target.closest("[data-close]") || event.target === dialog) closeDetail();
  });
  // ESC triggers the browser's native dialog cancel/close and never reaches
  // closeDetail(), so this is the one route where the event is the only signal.
  // afterClose() is idempotent, so the button path firing both is harmless.
  dialog.addEventListener("close", afterClose);
  dialog.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
    // Holding the key auto-repeats keydown; without this, each repeat would
    // still have opened a company (just onto a replaced history entry), so
    // holding ArrowRight would blow through the whole list in a blink.
    if (event.repeat) return;
    const index = roster.findIndex((c) => c.slug === current.slug);
    const next = event.key === "ArrowRight" ? index + 1 : index - 1;
    if (roster[next]) openDetail(roster[next], { replace: true });
  });

  document.querySelector("[data-grid]").addEventListener("click", (event) => {
    const cell = event.target.closest(".cell");
    if (!cell) return;
    const company = all.find((c) => c.slug === cell.dataset.slug);
    if (company) openDetail(company);
  });

  const routeFromHash = () => {
    const slug = location.hash.replace("#/", "");
    if (!slug) return;
    const company = all.find((c) => c.slug === slug);
    if (company) {
      // openDetail writes the hash itself, so this fires again a moment after
      // every open. Re-rendering the window that is already showing this exact
      // company would replay the entry animation, move focus back to the close
      // button and reset the roster the ←/→ keys are stepping through.
      if (dialog.open && current?.slug === slug) return;
      openDetail(company);
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
