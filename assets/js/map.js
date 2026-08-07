import { escapeHtml } from "./html.js";

// The visible halo shrinks down to r=18 for a single-company city, but every
// interactive control on this site keeps a >=44px hit target (see
// register.css's `min-height: 44px` on buttons, selects and chips). An SVG
// circle scales with the viewBox, not with CSS pixels, so there is no one
// radius that is exactly 44px at every viewport width — but 65 viewBox units
// covers the largest possible halo (r maxes out at 64, see MAX_RADIUS below)
// and comfortably clears 44px down to ~375px-wide viewports, which is this
// site's smallest realistic mobile breakpoint (register.css's `@media
// (max-width: 480px)`). Below that the target is still strictly bigger than
// the visible bubble, never smaller.
const MIN_HIT_RADIUS = 65;
const BASE_RADIUS = 18;
const MAX_RADIUS = 46; // added on top of BASE_RADIUS for the most-represented city

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

  const counts = companies.reduce((acc, c) => {
    const city = c.hq?.city;
    if (!city) return acc; // a record with a missing/malformed hq must not crash the map
    acc[city] = (acc[city] || 0) + 1;
    return acc;
  }, {});
  const known = Object.entries(counts).filter(([city]) => geoCities[city]);
  const unplaced = Object.entries(counts).filter(([city]) => !geoCities[city]);
  const max = Math.max(1, ...known.map(([, n]) => n));

  container.innerHTML = `
    <svg class="map__svg" viewBox="${escapeHtml(geo.viewBox)}" role="img"
         aria-label="German unicorns by headquarters city">
      ${geo.outline ? `<path class="map__outline" d="${escapeHtml(geo.outline)}"/>` : ""}
      ${known.map(([city, n]) => {
        const [x, y] = geoCities[city];
        const r = BASE_RADIUS + (n / max) * MAX_RADIUS;
        const hitR = Math.max(MIN_HIT_RADIUS, r);
        const safeCity = escapeHtml(city);
        const label = `${safeCity}, ${n} ${n === 1 ? "company" : "companies"}`;
        return `<g class="map__city" data-city="${safeCity}" tabindex="0" role="button"
                   aria-label="${label}">
          <circle cx="${x}" cy="${y}" r="${hitR}" class="map__hit"/>
          <circle cx="${x}" cy="${y}" r="${r}" class="map__halo"/>
          <circle cx="${x}" cy="${y}" r="4" class="map__pin"/>
          <text x="${x}" y="${y - r - 10}" class="map__label">${safeCity} · ${n}</text>
        </g>`;
      }).join("")}
    </svg>
    ${unplaced.length ? `<p class="map__note">Not shown on the map:
      ${unplaced.map(([city, n]) => `${escapeHtml(city)} (${n})`).join(", ")}</p>` : ""}`;

  const select = (node) => onSelectCity(node.dataset.city);
  container.querySelectorAll("[data-city]").forEach((node) => {
    node.addEventListener("click", () => select(node));
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") { event.preventDefault(); select(node); }
    });
  });
}
