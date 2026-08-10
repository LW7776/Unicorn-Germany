/* Two pictures of the register, drawn in the Companies intro.

   Both read their numbers straight out of data/companies.json's stats block,
   where tools/build.py settled them (crossingsByYear, sectorComposition). This
   module turns counts into geometry and adds nothing: no totals, no percentages,
   no rounding. That is the same rule register.js follows for labels, and it is
   why a chart here cannot quietly disagree with the grid below it.

   Two constraints shape how they are built.

   Colour never carries the meaning on its own. Every bar prints its own count,
   every segment is named in the legend beside its count, and each has a <title>
   for a pointer. Take all the colour out and both still say the same thing.

   Text is not inside the SVG. An <svg> scaled to its container scales its type
   with it, so a label sized to read at 1440 lands at seven or eight pixels at
   375 (the same trap map.js documents and works around). Here the graphics are
   SVG and the type is HTML in a grid that shares the graphic's column rhythm, so
   every label stays on the site's own type scale with its own 12px floor, at
   every width, with nothing to measure at runtime. */
import { escapeHtml } from "./html.js";

// Both charts are drawn in a 100x100 box and stretched to whatever the layout
// gives them (preserveAspectRatio="none"). Rectangles survive a non-uniform
// stretch unchanged, which is the whole reason the charts are rectangles.
const BOX = 100;
// Fraction of a year's column the bar occupies. The rest is the air that makes
// the columns read as separate years rather than as one histogram.
const BAR_WIDTH = 0.58;
// The gap punched between sector segments, in the same 0-100 units.
const SEGMENT_GAP = 0.35;

const SPOKEN = ["no companies", "one company", "two companies"];

function spokenCount(count) {
  return SPOKEN[count] || `${count} companies`;
}

/* The degradation, and the only thing rendered when a chart has nothing to draw:
   the figures as plain rows. An axis with no bars on it is a chart claiming to
   have measured something, which is worse than a short list saying what is
   known. Reached when the register is empty (build.py returns [] for both
   shapes) or, for the strip, when every year in range is a zero. */
function figureList(rows) {
  if (!rows.length) return "";
  return `<ul class="viz__figures">${rows.map(([label, value]) => `
    <li><span class="viz__figures-label">${escapeHtml(label)}</span>
        <span class="viz__figures-value">${escapeHtml(value)}</span></li>`).join("")}</ul>`;
}

function figure(modifier, title, note, body) {
  return `
    <figure class="viz viz--${modifier}" data-reveal>
      <figcaption class="viz__cap">
        <span class="label">${escapeHtml(title)}</span>
        <span class="viz__note">${escapeHtml(note)}</span>
      </figcaption>
      ${body}
    </figure>`;
}

/** The crossings strip: one column a year, from the first crossing to the last.
    A year in which nobody crossed is an empty track rather than a missing
    column, because the gaps are half of what this is for. */
function crossingsStrip(entries) {
  const total = entries.reduce((sum, entry) => sum + entry.count, 0);
  const note = `One column a year, from ${entries.length ? entries[0].year : ""} to ${
    entries.length ? entries[entries.length - 1].year : ""}. Every column is a year, empty ones included.`;
  const max = Math.max(0, ...entries.map((entry) => entry.count));
  if (!max) {
    return figure("crossings", "Crossings by year",
      "The year each company crossed a billion.",
      figureList(entries.map((entry) => [String(entry.year), String(entry.count)])));
  }

  const column = BOX / entries.length;
  const width = column * BAR_WIDTH;
  const bars = entries.map((entry, index) => {
    const x = index * column + (column - width) / 2;
    const height = (entry.count / max) * BOX;
    return `
      <rect class="strip__track" x="${x}" y="0" width="${width}" height="${BOX}"/>
      ${entry.count ? `<rect class="strip__bar" x="${x}" y="${BOX - height}" width="${width}" height="${height}"><title>${entry.year}, ${spokenCount(entry.count)}</title></rect>` : ""}`;
  }).join("");

  const spoken = entries.map((entry) => `${entry.year}, ${spokenCount(entry.count)}`).join(". ");
  const grid = `grid-template-columns:repeat(${entries.length},1fr)`;
  return figure("crossings", "Crossings by year", note, `
    <div class="strip">
      <ol class="strip__row strip__row--counts" style="${grid}">
        ${entries.map((entry) => `<li>${entry.count || "–"}</li>`).join("")}
      </ol>
      <svg class="strip__chart" viewBox="0 0 ${BOX} ${BOX}" preserveAspectRatio="none"
           role="img" aria-label="Companies crossing a billion, by year. ${escapeHtml(spoken)}. ${total} in total.">
        ${bars}
      </svg>
      <ol class="strip__row strip__row--years" style="${grid}" aria-hidden="true">
        ${entries.map((entry) => `<li>${entry.year}</li>`).join("")}
      </ol>
    </div>`);
}

/** The sector bar: the register divided once across the broad sectors.

    The fills ramp from --beam to --violet across the segments. That is a
    progression through the two accents the site already has, not a new palette,
    and DESIGN.md's "no third accent" holds: nothing here introduces a hue. The
    ramp is decoration in the strict sense, since the legend under the bar names
    every segment and prints its count. */
function sectorBar(entries) {
  const total = entries.reduce((sum, entry) => sum + entry.count, 0);
  if (!total) {
    return figure("sectors", "Sector composition", "The register divided across the broad sectors.",
      figureList(entries.map((entry) => [entry.sector, String(entry.count)])));
  }

  const last = Math.max(1, entries.length - 1);
  const tint = (index) =>
    `color-mix(in srgb, var(--violet) ${Math.round((index / last) * 100)}%, var(--beam))`;

  let x = 0;
  const segments = entries.map((entry, index) => {
    const width = (entry.count / total) * BOX;
    // The gap comes out of the segment's own width rather than being added
    // between them, so the widths still sum to the bar and the last segment
    // still ends flush with the right edge.
    const drawn = Math.max(0, width - (index === entries.length - 1 ? 0 : SEGMENT_GAP));
    const rect = `<rect x="${x}" y="0" width="${drawn}" height="${BOX}" fill="${tint(index)}"><title>${escapeHtml(entry.sector)}, ${spokenCount(entry.count)}</title></rect>`;
    x += width;
    return rect;
  }).join("");

  const spoken = entries.map((entry) => `${entry.sector}, ${spokenCount(entry.count)}`).join(". ");
  return figure("sectors", "Sector composition",
    `All ${total} placed once, under the sector each one leads with.`, `
    <svg class="sectorbar" viewBox="0 0 ${BOX} ${BOX}" preserveAspectRatio="none"
         role="img" aria-label="Sector composition. ${escapeHtml(spoken)}.">
      ${segments}
    </svg>
    <ul class="sectorlegend">
      ${entries.map((entry, index) => `
        <li class="sectorlegend__item">
          <span class="sectorlegend__swatch" style="background:${tint(index)}" aria-hidden="true"></span>
          <span class="sectorlegend__name">${escapeHtml(entry.sector)}</span>
          <span class="sectorlegend__count">${entry.count}</span>
        </li>`).join("")}
    </ul>`);
}

export function renderIntroVisualisations(container, stats) {
  if (!container) return;
  const crossings = stats?.crossingsByYear || [];
  const sectors = stats?.sectorComposition || [];
  // Nothing derived, nothing drawn. A shape with no entries gets no figure at
  // all rather than a caption over a blank frame, and an empty register
  // therefore leaves the whole block out of the page.
  container.innerHTML =
    (crossings.length ? crossingsStrip(crossings) : "") +
    (sectors.length ? sectorBar(sectors) : "");
}
