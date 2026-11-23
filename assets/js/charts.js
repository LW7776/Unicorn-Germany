// The page's drawings and its small motion.
//
// The curve and the bars are both made of real figures read from data/companies.json exactly as
// tools/build.py settled them. The only arithmetic here is cumulating the yearly crossings, which
// is the one thing a reader cannot do in their head while scrolling.
//
// Everything runs once, the first time it is seen, and never replays. A register is a reference
// people come back to, and motion that re-runs on every visit stops being an arrival and becomes a
// toll. Under prefers-reduced-motion nothing is scheduled at all and the finished state is painted
// directly, which is verifiable by counting requestAnimationFrame and Element.animate.
//
// Measured under reduced motion, both counts are zero on load and zero through entering the
// register. The one requestAnimationFrame that can appear afterwards is wireProgress coalescing a
// paint while the reader scrolls. That bar is a readout of where they already are rather than
// motion of its own, so it stays, and making it paint synchronously instead would mean doing
// layout work on every scroll event to satisfy a count.

const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)");
const EASE = "cubic-bezier(.23, 1, .32, 1)";

function esc(v) {
  return String(v == null ? "" : v).replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

/** Run `fn` the first time `el` is on screen, then stop watching it. */
function once(el, fn) {
  if (!el) return;
  if (!("IntersectionObserver" in window)) { fn(); return; }
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      io.disconnect();
      fn();
    }
  }, { threshold: 0.25 });
  io.observe(el);
}

/* ------------------------------------------------------------------ the curve */
export function renderCurve(host, crossings) {
  if (!host || !crossings || !crossings.length) return;

  // Cumulative, because the question a reader has is how many there are by a given year, not how
  // many arrived in it. A year nobody crossed in stays flat, which is the honest shape.
  let running = 0;
  const points = crossings.map((c) => ({ year: c.year, added: c.count, total: (running += c.count) }));

  const W = 920, H = 470, PAD_L = 10, PAD_R = 10, PAD_T = 18, PAD_B = 46;
  const max = points[points.length - 1].total;
  const x = (i) => PAD_L + (i / (points.length - 1)) * (W - PAD_L - PAD_R);
  const y = (v) => PAD_T + (1 - v / max) * (H - PAD_T - PAD_B);

  const line = points.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)} ${y(p.total).toFixed(1)}`).join(" ");
  const area = `${line} L${x(points.length - 1).toFixed(1)} ${H - PAD_B} L${x(0).toFixed(1)} ${H - PAD_B} Z`;

  host.innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="German companies past a billion, cumulative by year, ${points[0].year} to ${points[points.length - 1].year}">
      <defs>
        <linearGradient id="curve-stroke" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%"   stop-color="var(--indigo)"></stop>
          <stop offset="58%"  stop-color="var(--rose)"></stop>
          <stop offset="100%" stop-color="var(--amber)"></stop>
        </linearGradient>
        <linearGradient id="curve-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stop-color="var(--rose)" stop-opacity=".30"></stop>
          <stop offset="100%" stop-color="var(--indigo)" stop-opacity=".02"></stop>
        </linearGradient>
      </defs>
      <path class="curve__area" d="${area}" fill="url(#curve-fill)"></path>
      <path class="curve__line" d="${line}" fill="none" stroke="url(#curve-stroke)"
            stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></path>
      <g class="curve__dots">${points.map((p, i) =>
        `<circle cx="${x(i).toFixed(1)}" cy="${y(p.total).toFixed(1)}" r="4"></circle>`).join("")}</g>
      <g class="curve__years">${points.map((p, i) =>
        `<text x="${x(i).toFixed(1)}" y="${H - 16}">${esc(p.year)}</text>`).join("")}</g>
    </svg>
    <p class="curve__note note">Cumulative. ${esc(points[points.length - 1].total)} by ${esc(points[points.length - 1].year)}.</p>`;

  const path = host.querySelector(".curve__line");
  const areaEl = host.querySelector(".curve__area");
  const dots = host.querySelectorAll(".curve__dots circle");

  if (REDUCED.matches) return;   // the finished drawing is already in the DOM

  const len = path.getTotalLength();
  path.style.strokeDasharray = `${len}`;
  path.style.strokeDashoffset = `${len}`;
  areaEl.style.opacity = "0";
  dots.forEach((d) => { d.style.opacity = "0"; });

  once(host, () => {
    path.animate([{ strokeDashoffset: len }, { strokeDashoffset: 0 }],
      { duration: 1100, easing: EASE, fill: "forwards" });
    areaEl.animate([{ opacity: 0 }, { opacity: 1 }],
      { duration: 700, delay: 420, easing: EASE, fill: "forwards" });
    dots.forEach((d, i) => d.animate([{ opacity: 0, transform: "scale(.4)" }, { opacity: 1, transform: "none" }],
      { duration: 320, delay: 240 + i * 82, easing: EASE, fill: "forwards" }));
  });
}

/* ------------------------------------------------------------------ the charging bars */
export function renderSectors(host, sectors) {
  if (!host || !sectors || !sectors.length) return;
  const max = Math.max(...sectors.map((s) => s.count));

  host.innerHTML = sectors.map((s) => `
    <div class="bar">
      <div class="bar__row">
        <span class="bar__name">${esc(s.sector)}</span>
        <span class="bar__n fig">${esc(s.count)}</span>
      </div>
      <div class="bar__track"><div class="bar__fill" style="--pct:${((s.count / max) * 100).toFixed(1)}%"></div></div>
    </div>`).join("");

  const fills = host.querySelectorAll(".bar__fill");
  if (REDUCED.matches) { fills.forEach((f) => { f.style.width = "var(--pct)"; }); return; }

  fills.forEach((f) => { f.style.width = "0%"; });
  once(host, () => {
    fills.forEach((f, i) => {
      // Each bar charges to its own share. The stagger is short enough that the group reads as one
      // movement rather than eight separate ones.
      f.animate([{ width: "0%" }, { width: getComputedStyle(f).getPropertyValue("--pct").trim() }],
        { duration: 900, delay: i * 70, easing: EASE, fill: "forwards" });
    });
  });
}

/* ------------------------------------------------------------------ the counting figures */
export function countUp(el) {
  if (!el) return;
  const target = Number(el.dataset.count);
  if (!Number.isFinite(target)) return;
  const suffix = el.dataset.countSuffix || "";
  const prefix = el.dataset.countPrefix || "";
  const decimals = Number(el.dataset.countDecimals || 0);
  const show = (v) => { el.textContent = prefix + v.toFixed(decimals) + suffix; };

  if (REDUCED.matches) { show(target); return; }
  show(0);
  once(el, () => {
    const start = performance.now();
    const dur = 1000;
    const step = (now) => {
      const t = Math.min(1, (now - start) / dur);
      // The same ease-out the rest of the page moves on, so a number arriving matches a panel
      // arriving instead of being its own little event.
      show(target * (1 - Math.pow(1 - t, 3)));
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  });
}

/* ------------------------------------------------------------------ section reveals */
export function revealSections() {
  if (REDUCED.matches) return;
  document.querySelectorAll("[data-reveal]").forEach((el) => {
    el.style.opacity = "0";
    el.style.transform = "translateY(14px)";
    once(el, () => {
      el.animate([{ opacity: 0, transform: "translateY(14px)" }, { opacity: 1, transform: "none" }],
        { duration: 620, easing: EASE, fill: "forwards" });
    });
  });
}

/* ------------------------------------------------------------------ the scroll bar */
export function wireProgress() {
  const bar = document.querySelector("[data-progress]");
  if (!bar) return;
  let ticking = false;
  const paint = () => {
    const doc = document.documentElement;
    const span = doc.scrollHeight - doc.clientHeight;
    const pct = span > 0 ? Math.min(1, Math.max(0, doc.scrollTop / span)) : 0;
    // scaleX rather than width: it runs on the compositor, and this fires on every scroll frame.
    bar.style.transform = `scaleX(${pct})`;
    ticking = false;
  };
  // Passive and coalesced to one paint a frame, because a scroll handler that does layout work on
  // every event is the classic way to make a long page feel heavy.
  window.addEventListener("scroll", () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(paint);
  }, { passive: true });
  window.addEventListener("resize", paint, { passive: true });
  paint();
}
