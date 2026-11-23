// Aurora: the register as a lit room.
//
// Python still computes and JavaScript still renders. Every label, amount, date and percentage
// below is read from data/companies.json and data/funding.json exactly as tools/build.py settled
// it. The only arithmetic here is counting how many companies sit in a city for the map.

import { mountAuroraObject } from "./aurora-object.js";
import { renderCurve, renderSectors, countUp, revealSections, wireProgress } from "./charts.js";
import { playArrival, primeArrival } from "./arrival.js";

const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)");
const $ = (sel, root = document) => root.querySelector(sel);

function esc(value) {
  return String(value == null ? "" : value)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
function safeUrl(value) {
  try {
    const u = new URL(String(value), location.href);
    return (u.protocol === "https:" || u.protocol === "http:") ? u.href : null;
  } catch { return null; }
}
async function loadJson(path) {
  const response = await fetch(path, { cache: "no-cache" });
  if (!response.ok) throw new Error(`${path} ${response.status}`);
  return response.json();
}

/* ------------------------------------------------------------------ the landing */
function wireLanding() {
  const landing = $("#landing");
  const site = $("#site");
  const enter = $("#enter");
  if (!landing || !site || !enter) return;

  mountAuroraObject($("#landing-object"), { count: 40 });

  // The landing holds the page until it is pressed through, so the body must not scroll behind it.
  document.body.style.overflow = "hidden";

  let entered = false;
  function openSite() {
    if (entered) return;
    entered = true;
    const box = document.querySelector("[data-reg-box]");
    const grid = document.querySelector("[data-reg-grid]");

    // The grid goes before anything else moves. It is still behind the landing at this point, so
    // nobody sees it leave, and nobody sees the finished register sitting there waiting to be
    // assembled either.
    primeArrival(box);

    // The box is taller than most viewports once the heading and lede are above it, so pressing
    // through used to drop you with the bottom third of the arrival below the fold. Framing it
    // first is instant and happens under the landing.
    //
    // Centring it was the first attempt and it cut the lede through the middle of its glyphs
    // under the sticky header at phone width. The box's top edge is the thing to land on: just
    // under the nav, with air, and centred instead only when the whole box fits with room to
    // spare. getBoundingClientRect is relative to the viewport, so this reads before it writes.
    if (box) {
      const nav = document.querySelector(".nav");
      const navH = nav ? nav.getBoundingClientRect().height : 0;
      const top = box.getBoundingClientRect().top + window.scrollY;
      // Just under the nav, with air. Centring the box in the viewport was the first attempt and
      // it left the heading and its lede hanging half behind the sticky nav, sliced through the
      // glyphs at both widths. The head does not fit above a box this tall on a laptop screen, so
      // it is scrolled cleanly past rather than shown in half, and it is one flick back up.
      window.scrollTo({ top: Math.max(0, Math.round(top - navH - 20)), behavior: "auto" });
    }

    document.body.style.overflow = "";
    site.classList.add("is-on");

    if (REDUCED.matches) {
      landing.classList.add("is-gone");
      landing.hidden = true;
      const h = document.getElementById("register-h");
      if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
      playArrival({ box, grid });
      return;
    }

    // The landing leaves in two stages, which is what its CSS was written for: the words and the
    // object lift away first, then the whole plate goes. The burst starts between the two, so the
    // cards come up into a field that is still lit rather than onto a page already gone white.
    landing.classList.add("is-leaving");
    window.setTimeout(() => landing.classList.add("is-gone"), 260);
    window.setTimeout(() => {
      const h = document.getElementById("register-h");
      if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
      playArrival({ box, grid });
    }, 300);
    window.setTimeout(() => { landing.hidden = true; }, 900);
  }
  enter.addEventListener("click", openSite);

  // Arriving on a deep link skips the door rather than hiding the thing that was asked for.
  if (location.hash && location.hash !== "#top") openSite();
}

/* ------------------------------------------------------------------ the register */
function marksFor(company) {
  const d = company.display || {};
  const kinds = [];
  if (d.valuationUndisclosed) kinds.push(["undisclosed", "Undisclosed"]);
  if (company.valuation && company.valuation.disputed) kinds.push(["disputed", "Disputed"]);
  if (d.aged) kinds.push(["aged", "Aged"]);
  if (d.reported) kinds.push(["reported", "Reported"]);
  if (!kinds.length) return "";
  return `<span class="cell__marks">${kinds.map(([k, label]) =>
    `<span class="mark" data-kind="${k}" title="${label}"><span class="visually-hidden">${label}</span></span>`).join("")}</span>`;
}
function sourceById(company, id) {
  return (company.sources || []).find((s) => s.id === id) || null;
}

function cellHtml(company) {
  const d = company.display || {};
  const src = sourceById(company, (company.valuation || {}).source);
  const url = src && safeUrl(src.url);
  const logo = company.logo
    ? `<img src="${esc(company.logo)}" alt="" decoding="async">`
    : `<span class="cell__wordmark">${esc(company.name)}</span>`;
  // The card is a div with a stretched button rather than an anchor wrapping everything: an anchor
  // inside an anchor is invalid, and the proof link has to stay a real link.
  return `<div class="cell">
    <button class="cell__open" type="button" data-slug="${esc(company.slug)}">
      <span class="visually-hidden">Open ${esc(company.name)}</span>
    </button>
    <span class="cell__plate">${logo}</span>
    <p class="cell__name">${esc(company.name)}</p>
    <span class="cell__fig">${esc(d.valuationLabel || "Undisclosed")}</span>
    <span class="cell__meta">
      <span class="cell__date">${esc(d.valuationAsOf || "")}</span>
      ${url ? `<a class="cell__src" href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(src.publication)}</a>` : "<span></span>"}
    </span>
    ${marksFor(company)}
  </div>`;
}

function buildMap(geo, companies, onCity) {
  const counts = new Map();
  for (const c of companies) {
    const city = (c.hq || {}).city;
    if (city && geo.cities[city]) counts.set(city, (counts.get(city) || 0) + 1);
  }
  const placed = [...counts.entries()].sort((a, b) => b[1] - a[1]);
  const max = placed.length ? placed[0][1] : 1;
  // Several of these cities are neighbours at this scale. Gilching sits almost on Munich, and
  // Darmstadt, Alzenau and Mannheim are within a thumb's width of each other, so labels placed
  // blindly to the right of every dot landed on top of one another.
  //
  // Pins are already sorted biggest first, so each one in turn takes the best free position and
  // the smaller neighbour works around it. Boxes are in viewBox units: Spline Sans Mono is a true
  // monospace at 0.6em, and the label is 30 units, so every character is exactly 18 wide.
  const boxes = [];
  const CH = 18, LH = 34;
  const overlaps = (a) => boxes.some((b) =>
    a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y);

  const dots = placed.map(([city, n]) => {
    const [x, y] = geo.cities[city];
    // These are viewBox units, not pixels. Germany is 1400 units tall and the map fits that into
    // roughly 550px, so everything on it renders at about four tenths of the number written here.
    // Sized in pixels, the pins came out under 3px and the labels under 5px: a map nobody could
    // read, which is worse than no map.
    const r = 18 + Math.round((n / max) * 38);

    const w = city.length * CH;
    // Right of the dot first, then under, over, left, and further out in each direction. The dot
    // itself is reserved too, so a label never lands on a pin.
    const spots = [];
    for (const gap of [20, 64]) {
      spots.push(
        { x: x + r + gap, y: y - LH / 2, anchor: "start", ty: y + 9 },
        { x: x - w / 2, y: y + r + gap - 4, anchor: "middle", ty: y + r + gap + 22 },
        { x: x - w / 2, y: y - r - gap - 30, anchor: "middle", ty: y - r - gap - 4 },
        { x: x - r - gap - w, y: y - LH / 2, anchor: "end", ty: y + 9 });
    }
    const spot = spots.map((s) => ({ ...s, w, h: LH })).find((s) => !overlaps(s));

    // Gilching sits a few units from Munich on a map of the whole country, and there are places
    // where no position is free at all. Those pins go unlabelled rather than stacked: the dot
    // keeps its count, its focus ring and its full aria-label, so nothing is lost to anyone
    // reading or tapping, and the map stops printing two names over each other.
    if (spot) boxes.push(spot);
    boxes.push({ x: x - r - 23, y: y - r - 23, w: (r + 23) * 2, h: (r + 23) * 2 });

    return `<g class="map__city" tabindex="0" role="button" data-city="${esc(city)}"
              aria-label="${esc(city)}, ${n} ${n === 1 ? "company" : "companies"}">
      <circle class="map__ring" cx="${x}" cy="${y}" r="${r + 23}"></circle>
      <circle class="map__dot" cx="${x}" cy="${y}" r="${r}"></circle>
      <text class="map__n" x="${x}" y="${y + 9}">${n}</text>
      ${spot ? `<text class="map__label" x="${spot.anchor === "start" ? spot.x : spot.anchor === "end" ? spot.x + w : x}"
            y="${spot.ty}" text-anchor="${spot.anchor}">${esc(city)}</text>` : ""}
    </g>`;
  }).join("");
  const svg = `<svg viewBox="${esc(geo.viewBox)}" role="img" aria-label="Where the register's companies are based">
    <path class="map__land" d="${esc(geo.outline)}"></path>${dots}</svg>`;
  const host = $("[data-reg-map]");
  host.innerHTML = svg;
  host.querySelectorAll(".map__city").forEach((g) => {
    const pick = () => onCity(g.dataset.city);
    g.addEventListener("click", pick);
    g.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); }
    });
  });
}

function renderRegister(companies, geo, openSheet) {
  const grid = $("[data-reg-grid]");
  const map = $("[data-reg-map]");
  const search = $("#reg-search");
  const sector = $("#reg-sector");
  const count = $("[data-reg-count]");

  const sectors = [...new Set(companies.flatMap((c) => c.sectors || []))].sort();
  sector.innerHTML = `<option value="">All sectors</option>` +
    sectors.map((s) => `<option value="${esc(s)}">${esc(s)}</option>`).join("");

  let city = "";

  function visible() {
    const term = (search.value || "").trim().toLowerCase();
    const pick = sector.value;
    return companies.filter((c) => {
      if (pick && !(c.sectors || []).includes(pick)) return false;
      if (city && (c.hq || {}).city !== city) return false;
      if (!term) return true;
      return [c.name, c.niche, (c.hq || {}).city, ...(c.sectors || [])]
        .filter(Boolean).join(" ").toLowerCase().includes(term);
    });
  }

  function draw() {
    const list = visible();
    grid.innerHTML = list.length
      ? list.map(cellHtml).join("")
      : `<p class="lede">Nothing matches that. Clear the search to see all ${companies.length}.</p>`;
    const bits = [`${list.length} of ${companies.length}`];
    if (city) bits.push(`in ${city}`);
    count.textContent = bits.join(" ");
  }

  search.addEventListener("input", draw);
  sector.addEventListener("change", () => { city = ""; draw(); });

  document.querySelectorAll(".seg [data-view]").forEach((b) => {
    b.addEventListener("click", () => {
      document.querySelectorAll(".seg [data-view]").forEach((x) =>
        x.setAttribute("aria-pressed", String(x === b)));
      const isMap = b.dataset.view === "map";
      grid.hidden = isMap;
      map.hidden = !isMap;
      const scroller = document.querySelector("[data-reg-scroll]");
      if (scroller) scroller.scrollTop = 0;
    });
  });

  // Choosing a city on the map narrows the grid and shows it, which is what a reader wants from a
  // map: not a second place to read the same records, but a way into them.
  buildMap(geo, companies, (picked) => {
    city = picked === city ? "" : picked;
    draw();
    document.querySelectorAll(".seg [data-view]").forEach((x) =>
      x.setAttribute("aria-pressed", String(x.dataset.view === "grid")));
    grid.hidden = false;
    map.hidden = true;
    $("#register").scrollIntoView({ behavior: REDUCED.matches ? "auto" : "smooth", block: "start" });
  });

  grid.addEventListener("click", (e) => {
    const open = e.target.closest("[data-slug]");
    if (!open) return;
    const company = companies.find((c) => c.slug === open.dataset.slug);
    if (company) openSheet(company, open);
  });

  draw();
}

/* ------------------------------------------------------------------ the week */
function leadHtml(round) {
  const url = safeUrl(round.source && round.source.url);
  const people = [];
  if (round.foundersLabel) people.push(`Founded by ${esc(round.foundersLabel)}`);
  if (round.investorsLabel) people.push(esc(round.investorsLabel));
  return `<article class="lead">
    <div class="lead__head">
      <span class="lead__name">${esc(round.company)}</span>
      <span class="lead__fig fig">${esc(round.amountLabel || "")}</span>
    </div>
    <p class="lead__meta">${esc([round.stage, round.hq].filter(Boolean).join(" · "))}</p>
    ${round.text ? `<p class="lead__text">${esc(round.text)}</p>` : ""}
    ${people.length ? `<p class="lead__people">${people.join(" · ")}</p>` : ""}
    ${url ? `<p class="lead__src"><a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(round.source.publication)}</a>
       <span class="src__when">${esc(round.source.publishedOn)}</span></p>` : ""}
  </article>`;
}

function renderWeek(funding) {
  const host = $("[data-week]");
  const weeks = funding.weeks || [];
  if (!weeks.length) return;

  host.innerHTML = `
    <div class="week__leads" data-week-leads></div>
    <aside class="week__aside">
      <label class="field week__pick">
        <span class="visually-hidden">Choose a week</span>
        <select id="week-pick">${weeks.map((w, i) =>
          `<option value="${i}">${esc(w.rangeLabel || w.week)}</option>`).join("")}</select>
      </label>
      <div class="week__more" data-week-more></div>
    </aside>`;

  const leads = $("[data-week-leads]", host);
  const more = $("[data-week-more]", host);
  const pick = $("#week-pick", host);

  function draw() {
    const w = weeks[Number(pick.value) || 0];
    leads.innerHTML = (w.lead || []).map(leadHtml).join("");
    const rest = w.more || [];
    more.innerHTML = `<h3>Also raised, ${esc(w.roundCountLabel || "")}</h3>` + (rest.length
      ? rest.map((r) => `<div class="mrow">
          <span class="mrow__name">${esc(r.company)}</span>
          <span class="mrow__stage">${esc([r.stage, r.hq].filter(Boolean).join(" · "))}</span>
          <span class="mrow__fig">${esc(r.amountLabel || "")}</span>
        </div>`).join("")
      : `<p class="mrow__stage">Nothing else this week.</p>`);
  }
  pick.addEventListener("change", draw);
  draw();
}

/* ------------------------------------------------------------------ the detail sheet */
function wireSheet() {
  const sheet = $("[data-sheet]");
  const scrim = $("[data-scrim]");
  let lastFocus = null;

  function shut() {
    sheet.classList.remove("is-on");
    scrim.classList.remove("is-on");
    window.setTimeout(() => { sheet.hidden = true; scrim.hidden = true; }, REDUCED.matches ? 0 : 420);
    document.body.style.overflow = "";
    if (lastFocus && lastFocus.isConnected) lastFocus.focus({ preventScroll: true });
  }

  function open(company, trigger) {
    lastFocus = trigger || null;
    const d = company.display || {};
    const vSrc = sourceById(company, (company.valuation || {}).source);
    const quote = vSrc && vSrc.quote;
    const where = [(company.hq || {}).city, company.niche].filter(Boolean).join(" · ");
    const site = safeUrl(company.website);

    const facts = [
      ["Became a unicorn", d.becameUnicornLabel],
      ["Last round", [d.lastRoundLabel, d.lastRoundStage].filter(Boolean).join(" · ")],
      ["Founded", company.foundedYear],
      ["Founders", d.foundersLabel],
      ["Sectors", (company.sectors || []).join(", ")],
    ].filter(([, v]) => v);

    sheet.innerHTML = `<div class="sheet__in">
      <button class="sheet__close" type="button" aria-label="Close">
        <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true" fill="none">
          <path d="M3 3l8 8M11 3l-8 8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
        </svg>
      </button>
      ${company.logo ? `<span class="sheet__plate"><img src="${esc(company.logo)}" alt=""></span>` : ""}
      <h2 class="sheet__name">${esc(company.name)}</h2>
      ${where ? `<p class="sheet__where">${esc(where)}</p>` : ""}

      <p class="sheet__fig fig">${esc(d.valuationLabel || "Undisclosed")}</p>
      <p class="sheet__meta">
        <span class="cell__date">${esc(d.valuationAsOf || "")}${d.valuationRound ? " · " + esc(d.valuationRound) : ""}</span>
        ${vSrc && safeUrl(vSrc.url) ? `<a class="cell__src" href="${esc(safeUrl(vSrc.url))}" target="_blank" rel="noopener noreferrer">${esc(vSrc.publication)}</a>` : "<span></span>"}
      </p>

      ${quote ? `<div class="sheet__block"><h3>The sentence that proves it</h3>
        <blockquote class="sheet__quote">${esc(quote)}</blockquote></div>` : ""}

      ${company.thesis && company.thesis.solution ? `<div class="sheet__block"><h3>What it does</h3>
        <p>${esc(company.thesis.solution)}</p></div>` : ""}

      ${facts.length ? `<div class="sheet__block"><h3>On the record</h3>
        <dl class="sheet__dl">${facts.map(([k, v]) =>
          `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl></div>` : ""}

      <div class="sheet__block"><h3>Every source</h3>
        <div class="sheet__srcs">${(company.sources || []).map((s) => {
          const u = safeUrl(s.url);
          return `<div class="src">${u ? `<a href="${esc(u)}" target="_blank" rel="noopener noreferrer">${esc(s.title)}</a>` : esc(s.title)}
            <br><span class="src__when">${esc(s.publication)} · ${esc(s.publishedOn)}</span></div>`;
        }).join("")}</div></div>

      ${site ? `<a class="btn btn--ghost" href="${esc(site)}" target="_blank" rel="noopener noreferrer">${esc(d.websiteLabel || "Visit the site")}</a>` : ""}
    </div>`;

    sheet.hidden = false; scrim.hidden = false;
    // One frame so the transition has a start state to move from.
    requestAnimationFrame(() => { sheet.classList.add("is-on"); scrim.classList.add("is-on"); });
    document.body.style.overflow = "hidden";
    $(".sheet__close", sheet).addEventListener("click", shut);
    $(".sheet__close", sheet).focus({ preventScroll: true });
  }

  scrim.addEventListener("click", shut);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !sheet.hidden) shut(); });
  return open;
}

/* ------------------------------------------------------------------ boot */
async function boot() {
  wireLanding();
  const openSheet = wireSheet();

  const data = await loadJson("data/companies.json");
  window.__data = data;

  let geo = { viewBox: "0 0 1000 1400", outline: "", cities: {} };
  try { geo = await loadJson("data/geo/germany.json"); }
  catch (error) { console.error(error); }

  renderRegister(data.companies, geo, openSheet);

  const stats = data.stats || {};
  renderCurve($("[data-curve]"), stats.crossingsByYear);
  renderSectors($("[data-sectors]"), stats.sectorComposition);
  wireProgress();
  document.querySelectorAll("[data-count]").forEach(countUp);
  revealSections();

  // The ledger runs behind a lighter sourcing standard than the register, so its failure must not
  // take the register down with it. The register is the product.
  try {
    const funding = await loadJson("data/funding.json");
    window.__funding = funding;
    renderWeek(funding);
  } catch (error) {
    console.error(error);
    const host = $("[data-week]");
    if (host) host.innerHTML = `<p class="lede">The funding round-up could not be loaded. Reload the page, or <a href="https://github.com/LW7776/Unicorn-Germany/issues">report this on GitHub</a>.</p>`;
  }
}

boot().catch((error) => {
  console.error(error);
  const grid = $("[data-reg-grid]");
  if (grid) grid.innerHTML = `<p class="lede" role="alert">The register could not be loaded. Reload the page, or <a href="https://github.com/LW7776/Unicorn-Germany/issues">report this on GitHub</a>.</p>`;
});
