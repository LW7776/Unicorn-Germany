/* The weekly funding round-up: a selected week in full, with the available
   weeks as small selectable cards above it.

   Like register.js and detail.js, this renders precomputed labels — every
   figure, date, range and joined name list is settled in tools/build.py, so
   nothing here formats anything. What this file owns is escaping, the tab
   semantics of the week cards, and the one sentence that keeps this block's
   sourcing standard from being mistaken for the register's.

   Every interpolated value comes from data/funding.json, which is written by
   hand and by the weekly workflow — untrusted like every other data file. It
   goes through escapeHtml(), every attribute stays quoted, and a source URL is
   only rendered as a link when isSafeUrl() accepts its scheme. */
import { escapeHtml, isSafeUrl } from "./html.js";

/** The one line that has to keep two different promises apart. The register's
    claim is that every figure was checked against a verbatim quote; this
    block's is weaker on purpose, and a reader who assumes otherwise has been
    misled by us rather than by a source. It is stated in the block, not
    buried in About. */
const STANDARD =
  "Every round below carries a dated link to the reporting behind it, from the " +
  "same allowlisted publications as the register. The standard is lighter than " +
  "the register's: these figures are sourced and linked, not quote-checked.";

/** A source becomes a link only when its scheme is http(s); otherwise the
    title renders as plain text and the publication and date still show, so a
    bad URL degrades to a citation rather than to nothing. */
function sourceCite(source) {
  const title = escapeHtml(source.title);
  const link = isSafeUrl(source.url)
    ? `<a href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">${title} ↗</a>`
    : `<span>${title}</span>`;
  return `${link}
    <span class="roundup__cite">${escapeHtml(source.publication)} ·
      <span class="roundup__date">${escapeHtml(source.publishedLabel)}</span></span>`;
}

/** A round whose company is already in the register links to its entry. The
    match is on the exact name, case-insensitively — a substring match would
    tie every "Flix…" headline to Flix, which is the same noise tools/watch.py
    uses word boundaries to avoid. */
function registerLink(company, slugByName) {
  const slug = slugByName.get(company.toLowerCase());
  return slug
    ? ` <a class="roundup__tracked" href="#/${escapeHtml(slug)}"
           title="This company is in the register, open its entry">in the register</a>`
    : "";
}

/** "(at a €1 bn valuation)", or nothing at all. build.py leaves
    valuationLabel null when no source published a figure, and an empty
    parenthetical is better than "(at a — valuation)", which would read as a
    valuation of nothing. */
function valuationClause(round) {
  return round.valuationLabel
    ? ` <span class="roundup__valuation">(at a <span class="roundup__figure">${escapeHtml(round.valuationLabel)}</span> valuation)</span>`
    : "";
}

/** A conflicting figure for the same round, shown rather than reconciled.

    Sources disagree about round sizes more often than is comfortable — a
    company announces one number and the trade press reports another. The
    register's answer is `disputed`: publish the company's own figure for its
    own round and put the disagreement next to it, in amber, with its own link.
    This is the same answer in the same colour, because a reader who sees €35m
    here and €35m on the company card, with both noting the €30m press figure,
    learns something true; a reader who sees €35m in one place and €30m in the
    other just concludes the site is broken. */
function noteBadge(note) {
  if (!note) return "";
  return `<span class="roundup__note">
    <span class="roundup__note-badge">disputed</span>
    <span class="roundup__note-text">${escapeHtml(note.text)}</span>
    ${sourceCite(note.source)}
  </span>`;
}

function leadCard(round, slugByName) {
  const company = escapeHtml(round.company);
  // hq and stage are optional: a weekly recap line often gives a figure and a
  // country and nothing else. filter(Boolean) drops what the source withheld
  // rather than printing an em dash for it.
  const meta = [round.stage, round.hq].filter(Boolean).map(escapeHtml).join(" · ");
  const founders = round.foundersLabel
    ? `<p class="lead__people"><span class="label">Founded by</span>
         ${escapeHtml(round.foundersLabel)}</p>`
    : "";
  const investors = round.investorsLabel
    ? `<p class="lead__people"><span class="label">Investors</span>
         ${escapeHtml(round.investorsLabel)}</p>`
    : "";
  return `
    <article class="lead">
      <header class="lead__head">
        <h3 class="lead__company">${company}${registerLink(round.company, slugByName)}</h3>
        <p class="lead__figure">${escapeHtml(round.amountLabel)}${valuationClause(round)}</p>
        ${meta ? `<p class="lead__meta">${meta}</p>` : ""}
      </header>
      ${noteBadge(round.note)}
      <p class="prose lead__text">${escapeHtml(round.text)}</p>
      ${founders}${investors}
      <p class="lead__source">${sourceCite(round.source)}</p>
    </article>`;
}

/** The owner's format, exactly: "Company XXX, from Founders YYY, secured €ZZm
    (at a €AAm valuation)" — with the founders clause dropped, and the sentence
    closed up around it, when no source named them. Inventing a name to fill
    the template is the one thing the lighter standard still forbids. */
function moreItem(round, slugByName) {
  const company = `<span class="roundup__company">${escapeHtml(round.company)}</span>`;
  const from = round.foundersLabel
    ? `, from ${escapeHtml(round.foundersLabel)},`
    : "";
  return `
    <li class="roundup__item">
      <span class="roundup__line">${company}${from} secured
        <span class="roundup__figure">${escapeHtml(round.amountLabel)}</span>${valuationClause(round)}${registerLink(round.company, slugByName)}</span>
      <span class="roundup__meta">${sourceCite(round.source)}</span>
      ${noteBadge(round.note)}
    </li>`;
}

/** A week can arrive written up or merely listed — tools/validate_funding.py
    accepts both, and the weekly routine produces the listed shape when it has
    no API key to write prose with. A lead-less week must therefore not render
    an empty slot where a write-up would be: an empty container looks like a
    fault, and a reader who sees one concludes something failed rather than
    that nothing was written. So the panel says which kind of week this is, in
    a line, and goes straight to the list. */
const LISTED_ONLY =
  "No round was written up this week. What follows is every German round the " +
  "allowlisted feeds reported, listed with its source.";

function weekPanel(week, slugByName) {
  const written = week.lead.length > 0;
  const leads = written
    ? `<div class="roundup__leads${week.lead.length > 1 ? " roundup__leads--pair" : ""}">${
        week.lead.map((round) => leadCard(round, slugByName)).join("")}</div>`
    : `<p class="roundup__empty">${escapeHtml(LISTED_ONLY)}</p>`;
  // "Also raised" only reads correctly under a write-up. With nothing above
  // it, the list is the week rather than an addendum to it.
  const heading = written ? "Also raised this week" : "Raised this week";
  const more = week.more.length
    ? `<section class="roundup__more" aria-labelledby="roundup-more">
         <h3 class="label" id="roundup-more">${heading}</h3>
         <ul class="roundup__list">${week.more.map((round) => moreItem(round, slugByName)).join("")}</ul>
       </section>`
    // A week with no additional rounds says so rather than showing an empty
    // heading — "nothing else was reported" is information, and a bare heading
    // over blank space reads as a rendering fault.
    : `<p class="roundup__empty">No further German rounds were reported this week.</p>`;
  return `
    ${leads}
    ${more}`;
}

function weekCard(week, selected) {
  return `
    <button class="weekcard" type="button" role="tab"
            id="weekcard-${escapeHtml(week.week)}"
            aria-controls="roundup-panel"
            aria-selected="${selected ? "true" : "false"}"
            tabindex="${selected ? "0" : "-1"}"
            data-week="${escapeHtml(week.week)}">
      <span class="weekcard__id">${escapeHtml(week.shortLabel)}</span>
      <span class="weekcard__range">${escapeHtml(week.rangeLabel)}</span>
      <span class="weekcard__count">${escapeHtml(week.roundCount)} rounds</span>
    </button>`;
}

/** "2026-W30" out of "#funding/2026-W30", or null. A week is a thing worth
    linking to — "look at what Germany raised in W30" is a sentence people send
    each other — so selection is reflected in the URL and read back from it.
    The shape deliberately does not start with "#/", which detail.js owns for
    company slugs, so the two routers cannot claim each other's links. */
export function weekFromHash(hash) {
  const match = /^#funding\/(\d{4}-W\d{2})$/.exec(hash || "");
  return match ? match[1] : null;
}

export function renderFunding(container, funding, companies = []) {
  if (!container) return null;
  const weeks = funding?.weeks || [];
  if (!weeks.length) {
    container.innerHTML = `
      <div class="roundup__head">
        <p class="label">Weekly funding</p>
        <h2 class="roundup__title">German rounds, week by week.</h2>
        <p class="roundup__empty">No weeks have been published yet.</p>
      </div>`;
    return null;
  }

  const slugByName = new Map(
    companies.map((company) => [String(company.name).toLowerCase(), company.slug]));
  // build.py already ordered the weeks newest first and named the newest in
  // stats.latestWeek; the browser does not decide what "newest" means. A week
  // named in the URL wins over that default, and a URL naming a week that no
  // longer exists falls back to the newest rather than rendering nothing.
  const requested = weekFromHash(location.hash);
  const known = new Set(weeks.map((week) => week.week));
  let current = (requested && known.has(requested))
    ? requested
    : (funding.stats?.latestWeek || weeks[0].week);

  // data-reveal on the two blocks that are rendered once. Deliberately not on
  // the panel below them: it is re-rendered every time a week is selected, so
  // its contents are new elements each time and would fade in again on every
  // click — a reveal is an arrival, and arriving repeatedly is a flicker.
  container.innerHTML = `
    <div class="roundup__head" data-reveal>
      <p class="label">Weekly funding</p>
      <h2 class="roundup__title">German rounds, week by week.</h2>
      <p class="roundup__standard">${escapeHtml(STANDARD)}</p>
    </div>
    <div class="roundup__weeks" role="tablist" aria-label="Select a week" data-weeks data-reveal>
      ${weeks.map((week) => weekCard(week, week.week === current)).join("")}
    </div>
    <div class="roundup__panel" role="tabpanel" id="roundup-panel"
         aria-labelledby="weekcard-${escapeHtml(current)}" tabindex="0" data-panel></div>`;

  const panel = container.querySelector("[data-panel]");
  const cards = () => [...container.querySelectorAll("[data-week]")];

  const show = (weekId, { focus = false, route = false } = {}) => {
    const week = weeks.find((entry) => entry.week === weekId);
    if (!week) return;
    current = weekId;
    // Only a deliberate selection rewrites the URL, and it replaces rather than
    // pushes: flipping through weeks with the arrow keys is a lateral move
    // within one visit, so Back should leave the page rather than step back
    // through every week the visitor glanced at — the same reasoning
    // detail.js applies to its ←/→ navigation.
    if (route) history.replaceState(null, "", `#funding/${weekId}`);
    panel.innerHTML = weekPanel(week, slugByName);
    panel.setAttribute("aria-labelledby", `weekcard-${weekId}`);
    cards().forEach((card) => {
      const isCurrent = card.dataset.week === weekId;
      card.setAttribute("aria-selected", String(isCurrent));
      // Roving tabindex: only the selected week is a Tab stop, and the arrow
      // keys move between the rest — the same tablist contract controls.js's
      // sector chips follow for their radiogroup.
      card.tabIndex = isCurrent ? 0 : -1;
      if (isCurrent && focus) card.focus();
    });
  };

  container.querySelector("[data-weeks]").addEventListener("click", (event) => {
    const card = event.target.closest("[data-week]");
    if (card) show(card.dataset.week, { route: true });
  });

  container.querySelector("[data-weeks]").addEventListener("keydown", (event) => {
    const list = cards();
    const index = list.indexOf(document.activeElement);
    if (index === -1) return;
    const moves = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };
    let next;
    if (event.key in moves) {
      next = (index + moves[event.key] + list.length) % list.length;
    } else if (event.key === "Home") {
      next = 0;
    } else if (event.key === "End") {
      next = list.length - 1;
    } else {
      return;
    }
    event.preventDefault();
    show(list[next].dataset.week, { focus: true, route: true });
  });

  show(current);
  return { show, get week() { return current; } };
}
