// The register assembling itself.
//
// Pressing through the landing puts you on the site. Then, inside the register's own box, forty
// cards burst from the middle of the frame, hang there, and fly to the exact cell each one belongs
// to. The box clips them, so the whole thing happens in the window the register lives in rather
// than across the page.
//
// One card per company, carrying its name. It plays once. Under prefers-reduced-motion none of it
// is scheduled and the grid is simply there.

const EASE_OUT = "cubic-bezier(.23, 1, .32, 1)";
const EASE_IO = "cubic-bezier(.77, 0, .175, 1)";
const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)");

// A deterministic shuffle, so the scatter is the same every visit rather than a different accident
// each time. A register should not rearrange itself for no reason.
function rand(seed) {
  let s = seed >>> 0;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}

// Hiding the grid is split out from playing the burst, because the two happen at different
// moments. The grid has to be gone the instant the button is pressed, while the landing still
// covers it; the burst starts a little later, once the landing has begun to lift. Measured, the
// unsplit version showed the finished register for 745ms and then threw cards at it.
export function primeArrival(box) {
  if (box) box.classList.add("is-arriving");
}

export function playArrival({ box, grid, onDone }) {
  const done = () => { box.classList.remove("is-arriving"); onDone && onDone(); };
  if (!box || !grid) { done(); return; }

  const cells = [...grid.querySelectorAll(".cell")];
  if (REDUCED.matches || !cells.length) { done(); return; }

  box.classList.add("is-arriving");

  const bx = box.getBoundingClientRect();
  // The middle of the frame, a little above centre so the burst has room to fall into the grid.
  const ox = bx.width / 2;
  const oy = bx.height * 0.46;

  const layer = document.createElement("div");
  layer.className = "arrival";
  layer.setAttribute("aria-hidden", "true");

  const random = rand(20260401);
  const flights = cells.map((cell, i) => {
    const card = document.createElement("div");
    card.className = "fcard";
    // The name alone. A logo at this size and this many angles would be unreadable, and the names
    // are what a reader is actually scanning for.
    card.textContent = (cell.querySelector(".cell__name") || {}).textContent || "";
    card.style.left = `${ox}px`;
    card.style.top = `${oy}px`;
    layer.appendChild(card);

    const angle = random() * Math.PI * 2;
    const reach = 90 + random() * Math.min(bx.width, bx.height) * 0.42;
    return {
      card, i, cell,
      dx: Math.cos(angle) * reach,
      dy: Math.sin(angle) * reach * 0.74,
      dz: -360 + random() * 620,
      rx: -30 + random() * 60,
      ry: -40 + random() * 80,
      rz: -14 + random() * 28,
    };
  });

  box.appendChild(layer);

  const BURST = 620, HOLD = 520, SETTLE = 900;

  for (const f of flights) {
    f.card.animate([
      { transform: "translate(-50%, -50%) translate3d(0,0,0) scale(.16)", opacity: 0, offset: 0 },
      // Solid early: a card that spends its flight half transparent reads as a smudge rather than
      // as an object.
      { opacity: 1, offset: 0.24 },
      { transform: `translate(-50%, -50%) translate3d(${f.dx}px, ${f.dy}px, ${f.dz}px) rotateX(${f.rx}deg) rotateY(${f.ry}deg) rotateZ(${f.rz}deg) scale(1)`, opacity: 1, offset: 1 },
    ], { duration: BURST, delay: f.i * 6, easing: EASE_OUT, fill: "forwards" });
  }

  window.setTimeout(() => {
    const b = box.getBoundingClientRect();
    const landed = [];

    for (const f of flights) {
      // Measured against the cell itself, so a card lands on its record rather than near it.
      const r = f.cell.getBoundingClientRect();
      const tx = (r.left - b.left) + r.width / 2 - ox;
      const ty = (r.top - b.top) + r.height / 2 - oy;
      const from = `translate(-50%, -50%) translate3d(${f.dx}px, ${f.dy}px, ${f.dz}px) rotateX(${f.rx}deg) rotateY(${f.ry}deg) rotateZ(${f.rz}deg) scale(1)`;

      // Only eight or so of the forty cells are in the box at once. A card whose cell is below the
      // clip cannot land on it: it would fly out of the bottom of the frame and be cut off, which
      // is exactly what the first version did with thirty-two of the forty. Those cards instead
      // slide down to the bottom edge and go, which is the truth of it anyway. The rest of the
      // register is further down the scroller.
      const cy = oy + ty;
      if (cy > b.height - 24) {
        f.exits = true;
        f.card.animate([
          { transform: from, opacity: 1 },
          { transform: `translate(-50%, -50%) translate3d(${tx * 0.5}px, ${b.height - oy + 40}px, 0) rotateX(0) rotateY(0) rotateZ(0) scale(.96)`, opacity: 0 },
        ], { duration: Math.round(SETTLE * 0.72), delay: f.i * 7, easing: EASE_IO, fill: "forwards" });
        continue;
      }

      landed.push(f);
      f.card.animate([
        { transform: from },
        { transform: `translate(-50%, -50%) translate3d(${tx}px, ${ty}px, 0) rotateX(0) rotateY(0) rotateZ(0) scale(1)`,
          width: `${Math.round(r.width)}px`, height: `${Math.round(r.height)}px` },
      ], { duration: SETTLE, delay: f.i * 11, easing: EASE_IO, fill: "forwards" });

      // The flyer's name is centred on the card while the cell's name sits near its top, so a card
      // landing on its cell's bounds cannot bring the two into register: both were legible at
      // once, about 115px apart, and every company read as printed twice. The flyer's name goes
      // before it arrives, leaving the cell's own name to be the one that is there.
      f.card.animate([
        { color: "rgba(21, 19, 15, 1)", offset: 0 },
        { color: "rgba(21, 19, 15, 1)", offset: 0.42 },
        { color: "rgba(21, 19, 15, 0)", offset: 0.78 },
        { color: "rgba(21, 19, 15, 0)", offset: 1 },
      ], { duration: SETTLE, delay: f.i * 11, easing: "linear", fill: "forwards" });
    }

    // The real grid comes up underneath as the cards that landed fade off it. Only those are
    // faded here: the ones that left the frame have already taken themselves out.
    window.setTimeout(() => {
      done();
      landed.forEach((f, n) => {
        f.card.animate([{ opacity: 1 }, { opacity: 0 }],
          { duration: 320, delay: n * 14, easing: EASE_OUT, fill: "forwards" });
      });
      window.setTimeout(() => layer.remove(), SETTLE + 420);
    }, SETTLE * 0.72);
  }, BURST + HOLD);
}
