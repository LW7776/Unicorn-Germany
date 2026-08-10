/* The particle field IS the dataset: one point of light per company. The count
   is the only thing it takes from the register, and placement is seeded, so the
   same dataset always draws the same sky.

   Behind the points, two very slow pools of light drift across the field. They
   are on this canvas rather than a second one underneath it because a second
   canvas is a second full-viewport surface to composite for something that is
   already the cheapest thing on the page — and because "behind the constellation"
   is then just paint order, which cannot get out of sync with anything. */
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)");

/* Canvas takes colours as strings, so the palette has to be read out of the
   custom properties rather than referenced. Doing that here keeps DESIGN.md's
   "design tokens only" rule true of the drawn layer as well as the styled one —
   before this, three colours from the table were retyped as rgba() literals in
   the paint loop, which is exactly the drift the rule exists to prevent.
   The fallbacks are the same values and are only reachable if the stylesheet has
   not applied, in which case matching the tokens is the best guess available. */
const FALLBACK_RGB = { "--beam": "76,125,255", "--beam-text": "143,176,255", "--violet": "169,123,255" };

function tokenRgb(token) {
  const value = getComputedStyle(document.documentElement).getPropertyValue(token).trim();
  const hex = value.replace("#", "");
  if (!/^[0-9a-f]{6}$/i.test(hex)) return FALLBACK_RGB[token];
  return [0, 2, 4].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(",");
}

// The two ambient pools, as fractions of the field. Periods are in the tens of
// seconds because the brief is "very slow": at these numbers no pool completes a
// traverse inside the time anyone spends looking at the hero, so the field reads
// as breathing rather than as something moving across the screen.
const AURORA = [
  { token: "--beam", alpha: 0.08, x: [0.32, 0.16, 41000], y: [0.38, 0.12, 53000] },
  { token: "--violet", alpha: 0.06, x: [0.70, 0.14, 61000], y: [0.62, 0.13, 47000] },
];
// One pre-rendered sprite per pool, drawn once and then blitted. A radial
// gradient filled across the full canvas twice a frame is millions of shaded
// pixels on a retina backing store, for a shape that never changes — only its
// position does. A 256px sprite scaled up costs two drawImage calls instead, and
// the softness hides the upscale completely.
const SPRITE_PX = 256;

function auroraSprite(rgb, alpha) {
  const sprite = document.createElement("canvas");
  sprite.width = sprite.height = SPRITE_PX;
  const ctx = sprite.getContext("2d");
  const half = SPRITE_PX / 2;
  const gradient = ctx.createRadialGradient(half, half, 0, half, half, half);
  gradient.addColorStop(0, `rgba(${rgb},${alpha})`);
  // A middle stop, because a straight linear ramp to zero reads as a disc with a
  // visible edge at these sizes. This is the falloff that makes it a pool.
  gradient.addColorStop(0.5, `rgba(${rgb},${alpha * 0.34})`);
  gradient.addColorStop(1, `rgba(${rgb},0)`);
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, SPRITE_PX, SPRITE_PX);
  return sprite;
}

export class Constellation {
  constructor(canvas, count) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.count = count;
    this.running = false;
    this.points = [];
    this.starRgb = tokenRgb("--beam-text");
    this.linkRgb = tokenRgb("--beam");
    this.aurora = AURORA.map((pool) => ({ ...pool, sprite: auroraSprite(tokenRgb(pool.token), pool.alpha) }));
    this.resize();
    addEventListener("resize", () => this.resize(), { passive: true });
  }

  resize() {
    const previousW = this.w;
    const previousH = this.h;
    const dpr = Math.min(devicePixelRatio || 1, 2);
    const { width, height } = this.canvas.getBoundingClientRect();
    this.canvas.width = width * dpr;
    this.canvas.height = height * dpr;
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.w = width;
    this.h = height;

    if (!this.points.length) {
      this.seed();
    } else if (previousW && previousH) {
      // Keep each point where it was relative to the field, so nothing is
      // stranded off-screen when the viewport changes.
      const scaleX = this.w / previousW;
      const scaleY = this.h / previousH;
      for (const point of this.points) {
        point.x *= scaleX;
        point.y *= scaleY;
      }
    }

    // Assigning canvas.width clears the bitmap. When the loop is not running
    // (reduced motion), nothing else will ever repaint it.
    if (!this.running) this.paintStatic();
  }

  seed() {
    // Deterministic placement: the same dataset always yields the same sky.
    let seed = 7;
    const random = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    this.points = Array.from({ length: this.count }, () => ({
      x: random() * this.w,
      y: random() * this.h,
      r: 0.8 + random() * 1.6,
      vx: (random() - 0.5) * 0.08,
      vy: (random() - 0.5) * 0.08,
      phase: random() * Math.PI * 2,
    }));
  }

  start() {
    if (REDUCED.matches) return this.paintStatic();
    this.running = true;
    const frame = (time) => {
      if (!this.running) return;
      this.paint(time);
      requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  }

  stop() { this.running = false; }

  paintStatic() { this.paint(0); }

  /** The ambient field, painted first so everything else sits over it.

      `time` is 0 whenever the loop is not running, which is what makes reduced
      motion work here: paintStatic() calls paint(0), every pool evaluates at its
      own starting phase, and the field is drawn once and never touched again. No
      separate still-life code path, and nothing that can drift out of step with
      the moving one. */
  paintAurora(time) {
    const { ctx, w, h } = this;
    const radius = Math.max(w, h) * 0.62;
    for (const pool of this.aurora) {
      const [cx, ax, px] = pool.x;
      const [cy, ay, py] = pool.y;
      const x = w * (cx + ax * Math.sin(time / px));
      const y = h * (cy + ay * Math.cos(time / py));
      ctx.drawImage(pool.sprite, x - radius, y - radius, radius * 2, radius * 2);
    }
  }

  paint(time) {
    const { ctx, points, w, h } = this;
    ctx.clearRect(0, 0, w, h);
    this.paintAurora(time);

    ctx.strokeStyle = `rgba(${this.linkRgb},.13)`;
    ctx.lineWidth = 1;
    for (let i = 0; i < points.length; i++) {
      for (let j = i + 1; j < points.length; j++) {
        const dx = points[i].x - points[j].x;
        const dy = points[i].y - points[j].y;
        const distance = Math.hypot(dx, dy);
        if (distance < 150) {
          ctx.globalAlpha = 1 - distance / 150;
          ctx.beginPath();
          ctx.moveTo(points[i].x, points[i].y);
          ctx.lineTo(points[j].x, points[j].y);
          ctx.stroke();
        }
      }
    }
    ctx.globalAlpha = 1;

    for (const point of points) {
      if (this.running) {
        point.x += point.vx;
        point.y += point.vy;
        if (point.x < 0) { point.x = 0; point.vx = Math.abs(point.vx); }
        else if (point.x > w) { point.x = w; point.vx = -Math.abs(point.vx); }
        if (point.y < 0) { point.y = 0; point.vy = Math.abs(point.vy); }
        else if (point.y > h) { point.y = h; point.vy = -Math.abs(point.vy); }
      }
      const twinkle = 0.65 + 0.35 * Math.sin(time / 1400 + point.phase);
      const glow = ctx.createRadialGradient(
        point.x, point.y, 0, point.x, point.y, point.r * 6);
      glow.addColorStop(0, `rgba(${this.starRgb},${twinkle})`);
      glow.addColorStop(1, `rgba(${this.linkRgb},0)`);
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(point.x, point.y, point.r * 6, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}
