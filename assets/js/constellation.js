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
    const dpr = Math.min(devicePixelRatio || 1, 2);
    const { width, height } = this.canvas.getBoundingClientRect();
    this.canvas.width = width * dpr;
    this.canvas.height = height * dpr;
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.w = width;
    this.h = height;
    if (!this.points.length) this.seed();
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
    const point = this.points[index % this.points.length];
    const box = this.canvas.getBoundingClientRect();
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
        if (point.x < 0 || point.x > w) point.vx *= -1;
        if (point.y < 0 || point.y > h) point.vy *= -1;
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
