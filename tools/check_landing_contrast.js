// The landing's contrast gate, measured in a real browser.
//
//   playwright-cli run-code --filename=tools/check_landing_contrast.js
//
// tools/check_contrast.py checks the palette, which covers every surface on this site except one.
// The landing puts text over the aurora, and what sits behind a given word there depends on a
// blurred animated gradient, the veil laid over it, and where the text happens to end. That cannot
// be answered from a list of tokens, and trying to answer it from one is how the landing came to
// ship with its stat labels at 1.51:1 and its figures at 5.93:1 while the Python gate reported a
// clean pass.
//
// So this measures the page instead. For every text element on the landing it takes the element's
// own colour and the ground actually behind its glyphs, and holds the pair to the floor that
// element is held to: 7:1 for anything anyone reads, 4.5:1 for the labels --faint carries.
//
// It is a playwright-cli script rather than a Node module on purpose. This repo has no npm
// dependencies and is not going to get one, so the gate borrows the CLI that is already installed
// and leaves package.json alone. Run it by hand after touching the aurora, the veil, or the
// landing's copy. test_contrast.py asserts the veil exists, so it cannot be quietly deleted
// between runs, but only this says whether it is still doing its job.

async page => {
  const BASE = "http://localhost:9010";
  const VIEWPORTS = [[1440, 900], [390, 844]];
  const FLOORS = {
    "h1": 7.0,
    ".landing .lede": 7.0,
    ".landing .btn": 4.5,
  };

  const srgb = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  const lum = (c) => 0.2126 * srgb(c[0]) + 0.7152 * srgb(c[1]) + 0.0722 * srgb(c[2]);
  const ratio = (a, b) => {
    const la = lum(a), lb = lum(b);
    const hi = Math.max(la, lb), lo = Math.min(la, lb);
    return (hi + 0.05) / (lo + 0.05);
  };

  const lines = [];
  const failures = [];

  for (const [w, h] of VIEWPORTS) {
    await page.setViewportSize({ width: w, height: h });
    await page.goto(`${BASE}/?contrast=${w}`, { waitUntil: "load" });
    // One painted frame of the object, so nothing is measured against a blank canvas.
    await page.waitForTimeout(1400);

    const shot = await page.screenshot();
    const found = await page.evaluate(async (dataUrl) => {
      const img = new Image();
      img.src = dataUrl;
      await img.decode();
      const c = document.createElement("canvas");
      c.width = img.width; c.height = img.height;
      const ctx = c.getContext("2d");
      ctx.drawImage(img, 0, 0);
      const out = [];
      for (const sel of ["h1", ".landing .lede", ".landing .btn"]) {
        for (const el of document.querySelectorAll(sel)) {
          const r = el.getBoundingClientRect();
          if (!r.width || !r.height) continue;
          const d = ctx.getImageData(Math.round(r.left), Math.round(r.top),
                                     Math.round(r.width), Math.round(r.height)).data;
          let light = null, lightSum = -1, dark = null, darkSum = 1e9;
          for (let i = 0; i < d.length; i += 4) {
            const s = d[i] + d[i + 1] + d[i + 2];
            if (s > lightSum) { lightSum = s; light = [d[i], d[i + 1], d[i + 2]]; }
            if (s < darkSum) { darkSum = s; dark = [d[i], d[i + 1], d[i + 2]]; }
          }
          const cs = getComputedStyle(el);
          const colour = cs.color.replace(/[^\d,.]/g, "").split(",").slice(0, 3).map(Number);
          // Dark text on a light field: the ground is the lightest pixel in the box, which is what
          // shows between the glyphs. A filled button inverts that, so its ground is the darkest.
          const transparent = cs.backgroundColor === "rgba(0, 0, 0, 0)" || cs.backgroundColor === "transparent";
          out.push({ sel, colour, ground: transparent ? light : dark,
                     text: el.textContent.trim().replace(/\s+/g, " ").slice(0, 38) });
        }
      }
      return out;
    }, `data:image/png;base64,${shot.toString("base64")}`);

    lines.push(`${w}x${h}`);
    for (const p of found) {
      const floor = FLOORS[p.sel] || 4.5;
      const r = ratio(p.colour, p.ground);
      const ok = r >= floor;
      if (!ok) failures.push(`${w}x${h} ${p.sel} "${p.text}" is ${r.toFixed(2)}:1, floor ${floor}`);
      lines.push(`  ${p.sel.padEnd(16)} ${r.toFixed(2).padStart(6)}:1  floor ${floor}  ${ok ? "PASS" : "FAIL"}  ${p.text}`);
    }
  }

  if (failures.length) {
    lines.push("");
    for (const f of failures) lines.push("FAIL: " + f);
    lines.push(`\nlanding contrast FAILED: ${failures.length}`);
  } else {
    lines.push("\nlanding contrast PASS at every viewport");
  }
  return lines.join("\n");
}
