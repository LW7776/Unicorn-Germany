/* The particle field IS the dataset: one point of light per company.
   Points keep stable indices so transition.js can fly each one to its own grid cell. */
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)");

export class Constellation {
  constructor(canvas, count) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.count = count;
    this.running = false;
    this.points = [];
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

  pointAt(index) {
    const box = this.canvas.getBoundingClientRect();
    // No companies yet (empty dataset) means no points to index into — fall back
    // to the canvas centre so callers (Task 6's FLIP) never dereference undefined.
    if (!this.points.length) {
      return { x: box.left + this.w / 2, y: box.top + this.h / 2 };
    }
    const length = this.points.length;
    // % is remainder, not modulo, in JS — negative index needs an explicit
    // wrap so this never indexes past the array and returns undefined.
    const point = this.points[((index % length) + length) % length];
    return { x: box.left + point.x, y: box.top + point.y };
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

  paint(time) {
    const { ctx, points, w, h } = this;
    ctx.clearRect(0, 0, w, h);

    ctx.strokeStyle = "rgba(76,125,255,.13)";
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
      glow.addColorStop(0, `rgba(143,176,255,${twinkle})`);
      glow.addColorStop(1, "rgba(76,125,255,0)");
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(point.x, point.y, point.r * 6, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}
