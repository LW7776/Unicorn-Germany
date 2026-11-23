// The landing object.
//
// Forty thin plates, one for every company on the register, standing on a common axis and turning
// slowly inside the aurora. The field is the light: each plate takes its fill from where it sits in
// that field, so the object and the ground are one device rather than two competing ones. A single
// plate carries the emissive edge.
//
// This is a few hundred lines of projected polygons on a 2D canvas rather than three.js, because
// three.js is about 420KB gzipped and this object is the only 3D on the site. A register whose
// premise is that it costs nothing to run should not ship two megabytes to turn one shape.
//
// Nothing is scheduled under prefers-reduced-motion: the object paints one frame and stops, which
// is verifiable by counting requestAnimationFrame rather than by looking at it.

const TAU = Math.PI * 2;

// The aurora's own three lights, sampled by angle so a plate facing the rose side reads rose.
const LIGHTS = [
  { a: 0.62, rgb: [61, 78, 245] },    // indigo, lower left
  { a: 2.20, rgb: [242, 86, 126] },   // rose, lower right
  { a: 4.10, rgb: [242, 163, 60] },   // amber, under
];
// The unlit tone of a plate. It used to be [252, 250, 247], which is bone, so an unlit plate was
// the page: measured against the ground, the plates differed by at most 42 of 255 and several by
// under 15, and the object read as a pale fan rather than as a solid standing in the light. A
// plate facing away from every light still has to be a surface.
const BASE = [214, 208, 200];
const EMISSIVE = [150, 178, 255];

function mix(a, b, t) {
  return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
}
function css(rgb, alpha) {
  return `rgba(${rgb[0] | 0},${rgb[1] | 0},${rgb[2] | 0},${alpha})`;
}

// How much of each light reaches a normal pointing at `angle`, as a plain cosine falloff.
function lightAt(angle) {
  let out = BASE.slice();
  for (const l of LIGHTS) {
    let d = Math.abs(((angle - l.a + Math.PI) % TAU + TAU) % TAU - Math.PI);
    const k = Math.max(0, 1 - d / 1.9);
    out = mix(out, l.rgb, k * 0.78);
  }
  return out;
}

export function mountAuroraObject(canvas, options = {}) {
  if (!canvas || !canvas.getContext) return null;
  const ctx = canvas.getContext("2d");
  if (!ctx) return null;

  const count = options.count || 40;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");

  // One plate per company. Each is a thin quad standing on the axis, fanned around it and given a
  // little vertical drift so the silhouette is a soft bloom rather than a tin can.
  // A first pass varied radius, height and offset per plate and produced two chaotic stacks rather
  // than one object. The form only reads when the blades agree: one radius, one height, one twist,
  // and a shallow wave so the ring breathes instead of sitting flat.
  const plates = [];
  for (let i = 0; i < count; i++) {
    const t = i / count;
    plates.push({
      a: t * TAU,                        // its angle around the axis
      r0: 0.40,                          // inner radius, constant
      r1: 0.98,                          // outer radius, constant
      y: Math.sin(t * TAU * 2) * 0.07,   // a shallow wave around the equator
      h: 0.115,                          // blade half-height, constant and thin
      twist: 0.42,                       // every blade pitched the same way: a turbine, not a fan
      lit: i === Math.floor(count * 0.18),
    });
  }

  let w = 0, h = 0, dpr = 1, raf = 0, spin = 0, running = false;

  function resize() {
    const rect = canvas.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = Math.max(1, Math.round(rect.width));
    h = Math.max(1, Math.round(rect.height));
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  // A plain perspective projection. Nothing here needs a matrix library.
  function project(x, y, z, cx, cy, scale) {
    const d = 3.2;
    const k = d / (d + z);
    return [cx + x * scale * k, cy + y * scale * k, k];
  }

  function frame(time) {
    const cx = w / 2;
    const cy = h / 2;
    const scale = Math.min(w, h) * 0.34;
    const tilt = -0.62;  // steep enough to read as a ring rather than a bowtie seen edge-on

    ctx.clearRect(0, 0, w, h);

    const quads = [];
    for (const p of plates) {
      const a = p.a + spin;
      const sa = Math.sin(a), ca = Math.cos(a);
      // Four corners of the plate, in object space, before the tilt.
      // The blade is pitched about its own radial axis by `twist`, so the inner edge sits high and
      // the outer edge low. That is what turns a flat ring into something that catches the light
      // differently all the way round.
      const tw = p.twist;
      const corners = [
        [ca * p.r0, p.y - p.h - tw * 0.10, sa * p.r0],
        [ca * p.r1, p.y - p.h + tw * 0.22, sa * p.r1],
        [ca * p.r1, p.y + p.h + tw * 0.22, sa * p.r1],
        [ca * p.r0, p.y + p.h - tw * 0.10, sa * p.r0],
      ].map(([x, y, z]) => {
        const yy = y * Math.cos(tilt) - z * Math.sin(tilt);
        const zz = y * Math.sin(tilt) + z * Math.cos(tilt);
        return project(x, yy, zz, cx, cy, scale);
      });
      const depth = (corners[0][2] + corners[2][2]) / 2;
      quads.push({ p, corners, depth, a });
    }

    // Painter's algorithm: the far plates first, so the near ones lie over them.
    quads.sort((q1, q2) => q1.depth - q2.depth);

    for (const q of quads) {
      const near = (q.depth - 0.72) / 0.5;           // 0 at the back, 1 at the front
      const tone = lightAt(q.a % TAU);
      const [x0, y0] = q.corners[0];
      const [x2, y2] = q.corners[2];

      const g = ctx.createLinearGradient(x0, y0, x2, y2);
      // Opaque enough to be a surface. The near edge of a plate catches the light and the far
      // edge falls into its own tone, which is what makes forty flat quads read as one turning
      // solid rather than as overlapping tints.
      g.addColorStop(0, css(mix(tone, [255, 255, 255], 0.52), 0.55 + near * 0.40));
      g.addColorStop(1, css(mix(tone, [96, 92, 104], 0.22), 0.40 + near * 0.38));

      ctx.beginPath();
      ctx.moveTo(q.corners[0][0], q.corners[0][1]);
      for (let i = 1; i < 4; i++) ctx.lineTo(q.corners[i][0], q.corners[i][1]);
      ctx.closePath();
      ctx.fillStyle = g;
      ctx.fill();

      // The one lit edge. It is a stroke on a single plate, not a glow on everything: the whole
      // point of an emissive edge is that exactly one thing is emitting. It was a thin outline
      // before, which read as a stray wireframe rather than as something giving off light, so it
      // now carries its own bloom and is drawn bright over its own fill.
      if (q.p.lit) {
        ctx.save();
        ctx.shadowColor = css(EMISSIVE, 0.95);
        ctx.shadowBlur = 22 + near * 20;
        ctx.strokeStyle = css(mix(EMISSIVE, [255, 255, 255], 0.55), 0.85 + near * 0.15);
        ctx.lineWidth = 2.4;
        ctx.stroke();
        // Twice, so the bloom accumulates into a glow instead of a halo.
        ctx.shadowBlur = 9 + near * 8;
        ctx.stroke();
        ctx.restore();
      } else {
        ctx.strokeStyle = css(mix(tone, [255, 255, 255], 0.72), 0.34 + near * 0.34);
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    }

    if (running) {
      spin += 0.0016;
      raf = requestAnimationFrame(frame);
    }
  }

  function start() {
    if (running) return;
    // Under reduced motion the object is a still life: one frame, no loop, nothing scheduled.
    if (reduced.matches) { resize(); frame(0); return; }
    running = true;
    raf = requestAnimationFrame(frame);
  }
  function stop() {
    running = false;
    if (raf) cancelAnimationFrame(raf);
    raf = 0;
  }

  resize();
  start();

  const onResize = () => { resize(); if (!running) frame(0); };
  window.addEventListener("resize", onResize, { passive: true });
  reduced.addEventListener("change", () => { stop(); start(); });
  // Nothing turns while the tab is hidden. A register left open in a background tab should not
  // hold a frame loop for hours.
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stop(); else start();
  });

  return { start, stop, destroy() { stop(); window.removeEventListener("resize", onResize); } };
}
