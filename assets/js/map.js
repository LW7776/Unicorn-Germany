import { escapeHtml } from "./html.js";

const BASE_RADIUS = 18;
const MAX_RADIUS = 46; // added on top of BASE_RADIUS for the most-represented city
// Half of the site's 44px minimum interactive target (register.css's
// `min-height: 44px` on buttons, selects and chips) — halved because it's
// used as a circle radius, not a diameter.
const MIN_HIT_TARGET_PX = 44;
// Used only if the SVG can't be measured (e.g. rendered with zero width);
// matches this file's previous fixed-radius behaviour as a safety net.
const FALLBACK_HIT_RADIUS = 65;
// Fallback only for a viewBox string that's missing or malformed — matches
// tools/fetch_geo.py's own VIEW_W/VIEW_H. Not used on any real, current
// data/geo/germany.json, which always carries "0 0 1000 1400".
const FALLBACK_VIEWBOX = { minX: 0, minY: 0, width: 1000, height: 1400 };

/** Parses an SVG viewBox string ("minX minY width height") into its four
    numbers. Reused for both the bounds check below and the hit-target scale
    calculation further down, so the two can never read a different box —
    and so neither one hard-codes 1000x1400, which would silently go stale
    if data/geo/germany.json were ever regenerated at another size. */
function parseViewBox(viewBox) {
  const parts = (viewBox || "").trim().split(/\s+/).map(Number);
  if (parts.length !== 4 || parts.some((n) => !Number.isFinite(n))) return FALLBACK_VIEWBOX;
  const [minX, minY, width, height] = parts;
  return { minX, minY, width, height };
}

/** company.hq.city comes from data/companies.json, an automated pipeline's
    output — untrusted the same as every other field rendered from it. Every
    interpolation below (data-city, aria-label, the visible label text, and
    the "not shown" note) goes through escapeHtml, and every attribute stays
    quoted. */
export async function renderMap(container, companies, { onSelectCity }) {
  const response = await fetch("data/geo/germany.json", { cache: "no-cache" });
  if (!response.ok) throw new Error(`data/geo/germany.json ${response.status}`);
  const geo = await response.json();
  const geoCities = geo.cities || {};
  const viewBox = parseViewBox(geo.viewBox);

  // A city counts as placeable only if this file has coordinates for it AND
  // those coordinates actually fall inside the map's own viewBox. The two
  // used to be the same check, but a projection built for Germany's bounding
  // box can produce a coordinate for a real, named city (e.g. Dash0's New
  // York) that lands thousands of units outside it — "has an entry" is not
  // the same guarantee as "is on the map". The SVG clips anything outside
  // its viewBox by default, so treating an out-of-bounds point as `known`
  // would silently drop its bubble with no visible trace anywhere on the
  // page — worse than the honest "Not shown on the map" fallback this check
  // routes it to instead, indistinguishable here from a city this file never
  // got coordinates for at all.
  function isPlaceable(city) {
    const coords = geoCities[city];
    if (!coords) return false;
    const [x, y] = coords;
    return x >= viewBox.minX && x <= viewBox.minX + viewBox.width &&
      y >= viewBox.minY && y <= viewBox.minY + viewBox.height;
  }

  // A company with no hq at all, or an hq with no city, isn't the same as a
  // company whose city just isn't on the map — it's missing data, and the
  // site's rule is that missing data is shown, never silently dropped. Count
  // it separately from `unplaced` (which is a real, named city this file
  // either has no coordinates for, or whose coordinates fall outside the
  // viewBox — both render identically, as "not shown", because both mean
  // the same thing to a reader: this map cannot place this city).
  let missingLocation = 0;
  const counts = companies.reduce((acc, c) => {
    const city = c.hq?.city;
    if (!city) { missingLocation += 1; return acc; }
    acc[city] = (acc[city] || 0) + 1;
    return acc;
  }, {});
  const known = Object.entries(counts).filter(([city]) => isPlaceable(city));
  const unplaced = Object.entries(counts).filter(([city]) => !isPlaceable(city));
  const max = Math.max(1, ...known.map(([, n]) => n));

  // Render the outline (and an empty <svg>) first so its actual rendered CSS
  // width can be measured below — the viewBox scales content independent of
  // what's inside it, so this measurement doesn't need the city bubbles to
  // exist yet, and doesn't need a second layout pass after adding them.
  container.innerHTML = `
    <svg class="map__svg" viewBox="${escapeHtml(geo.viewBox)}" role="img"
         aria-label="German unicorns by headquarters city">
      ${geo.outline ? `<path class="map__outline" d="${escapeHtml(geo.outline)}"/>` : ""}
    </svg>`;
  const svg = container.querySelector(".map__svg");
  const renderedWidth = svg.getBoundingClientRect().width;
  const scale = renderedWidth / viewBox.width;
  // The 44px target converted from CSS pixels into *this render's* viewBox
  // units. Unlike a fixed viewBox-unit radius, this actually tracks 44px at
  // whatever width the SVG is currently drawn at, instead of only being
  // correct at one particular viewport width.
  const targetHitRadius = scale > 0
    ? (MIN_HIT_TARGET_PX / 2) / scale
    : FALLBACK_HIT_RADIUS;

  const positioned = known.map(([city, n]) => {
    const [x, y] = geoCities[city];
    return { city, n, x, y, visibleRadius: BASE_RADIUS + (n / max) * MAX_RADIUS };
  });

  // Nearest-neighbour distance among the cities actually being drawn (a city
  // with zero companies today has no bubble, so it isn't a constraint).
  // Capping each hit radius at half that distance means it can never reach
  // past the midpoint into a neighbour's territory — the two circles can
  // touch exactly at the midpoint but never cross it, so a click nearest to
  // city B can never be captured by city A's hit area, regardless of paint
  // order. The visible bubble itself is never shrunk to make room; only the
  // invisible hit area is capped, and never below the bubble's own radius.
  const sized = positioned.map((entry) => {
    let nearest = Infinity;
    for (const other of positioned) {
      if (other === entry) continue;
      const distance = Math.hypot(entry.x - other.x, entry.y - other.y);
      if (distance < nearest) nearest = distance;
    }
    const neighbourCap = Number.isFinite(nearest) ? nearest / 2 : Infinity;
    const hitRadius = Math.max(entry.visibleRadius, Math.min(targetHitRadius, neighbourCap));
    return { ...entry, hitRadius, reachedTarget: hitRadius >= targetHitRadius - 0.05 };
  });

  // SVG paints in document order, so without this the winner of an
  // overlapping click is whichever bubble happens to come later in
  // `companies` — an accident of data order, not geography. Painting the
  // smallest hit targets last puts them on top, so a small city sitting
  // inside a larger neighbour's halo stays reachable.
  sized.sort((a, b) => b.hitRadius - a.hitRadius);

  const anyCramped = sized.some((entry) => !entry.reachedTarget);

  svg.insertAdjacentHTML("beforeend", sized.map(({ city, n, x, y, visibleRadius, hitRadius }) => {
    const safeCity = escapeHtml(city);
    const label = `${safeCity}, ${n} ${n === 1 ? "company" : "companies"}`;
    return `<g class="map__city" data-city="${safeCity}" tabindex="0" role="button"
               aria-label="${label}">
      <circle cx="${x}" cy="${y}" r="${hitRadius}" class="map__hit"/>
      <circle cx="${x}" cy="${y}" r="${visibleRadius}" class="map__halo"/>
      <circle cx="${x}" cy="${y}" r="4" class="map__pin"/>
      <text x="${x}" y="${y - visibleRadius - 10}" class="map__label">${safeCity} · ${n}</text>
    </g>`;
  }).join(""));

  // Capping each hit radius at the neighbour's midpoint (above) keeps a
  // click on Heidelberg's own bubble from ever landing inside Mannheim's
  // hit-circle — but the floor that guarantees a hit area is never smaller
  // than its own visible bubble can still push a *large* city's hit circle
  // (e.g. Mannheim, r=64 for its 2 companies) well past that same midpoint
  // from the other side, since the floor is a harder requirement than the
  // cap. Concretely, with two companies in Mannheim and one in Heidelberg
  // (25.1 viewBox units apart), Heidelberg's hit circle is floored up to
  // r=41 — bigger than the 25.1 unit gap — so it geometrically covers
  // Mannheim's own centre point too. Paint order alone can't fix a
  // genuinely-too-large hit circle, so instead of trusting whichever <g>
  // the browser's native top-most-element hit-test happens to report,
  // resolveCity re-checks geometry at click time: among every city whose
  // hit circle contains the click point, the one whose *centre* is closest
  // to the click wins. A click on Mannheim's own dot is distance 0 from
  // Mannheim and 25.1 from Heidelberg, so Mannheim wins regardless of which
  // element's hit circle happened to paint on top there.
  function resolveCity(event, fallbackCity) {
    const ctm = svg.getScreenCTM();
    if (!ctm) return fallbackCity;
    const point = svg.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    const local = point.matrixTransform(ctm.inverse());
    let best = null;
    let bestDistance = Infinity;
    for (const entry of sized) {
      const distance = Math.hypot(local.x - entry.x, local.y - entry.y);
      if (distance <= entry.hitRadius && distance < bestDistance) {
        best = entry.city;
        bestDistance = distance;
      }
    }
    return best ?? fallbackCity;
  }

  const notFound = [
    ...unplaced.map(([city, n]) => `${escapeHtml(city)} (${n})`),
    ...(missingLocation ? [`Location not recorded (${missingLocation})`] : []),
  ];
  let extraHtml = notFound.length
    ? `<p class="map__note">Not shown on the map: ${notFound.join(", ")}</p>` : "";
  if (anyCramped) {
    // Finding 3's genuine trade-off: on narrow viewports (or with cities
    // this close together at any width — e.g. Mannheim/Heidelberg are ~25
    // viewBox units apart, closer than a 44px target needs even at desktop
    // width) the 44px target and "never steal a neighbour's click" cannot
    // both fully hold. This implementation always prefers not stealing: the
    // neighbourCap clamp plus resolveCity's nearest-centre tie-break (above)
    // together mean a crowded city's hit target can still land smaller than
    // 44px, but it never resolves to the wrong city — clicking it is just
    // more fiddly, not incorrect. This note is the visible cost of that
    // trade-off; Task 19's accessibility pass should keep this behaviour
    // (correct-but-small) rather than loosen the clamp to hit 44px exactly
    // at the cost of occasional misfires.
    extraHtml += `<p class="map__note map__note--hint">Cities close together on the map ` +
      `may be easier to pick from the city dropdown above.</p>`;
  }
  container.insertAdjacentHTML("beforeend", extraHtml);

  container.querySelectorAll("[data-city]").forEach((node) => {
    // Mouse/touch: the point that was actually clicked may sit inside more
    // than one city's hit circle (see resolveCity above) — resolve by
    // nearest centre rather than trusting which <g> the event landed on.
    node.addEventListener("click", (event) => onSelectCity(resolveCity(event, node.dataset.city)));
    // Keyboard: the focused element unambiguously identifies one city —
    // there's no click point to disambiguate, so no geometry needed here.
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        onSelectCity(node.dataset.city);
      }
    });
  });
}
