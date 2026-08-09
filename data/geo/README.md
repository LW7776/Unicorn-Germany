# `data/geo/germany.json` provenance

- **Source**: `https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson`
  (the `datasets/geo-countries` project on GitHub — plain GeoJSON, one feature
  per country, derived from Natural Earth admin-0 country boundaries).
- **Fetched**: 2026-08-07.
- **License**: Natural Earth data is public domain (no attribution required);
  the `geo-countries` repackaging carries a PDDL/public-domain-equivalent
  license. Safe to redistribute the derived, simplified output committed here.
- **Selection**: the source's Germany feature (`ISO3166-1-Alpha-3 == "DEU"`)
  is a `MultiPolygon` of 22 rings. This build keeps only the largest ring by
  shoelace area — the mainland — and drops the other 21, which are North
  Sea/Baltic islands (e.g. Rügen, Usedom, Fehmarn, Sylt, Borkum and similar
  smaller islands); together they total 632 points. Dropping them keeps the
  outline a single closed path with no separate island shapes to render.
- **Projection**: `tools/fetch_geo.py:build_projection` — a single function
  used for both the outline and every city coordinate, so they can never
  drift apart. It is a simple equirectangular projection: longitude is
  scaled by `cos(mean latitude)` so a degree of longitude and a degree of
  latitude represent comparable ground distance at Germany's latitude, then
  the whole thing is scaled *uniformly* (not stretched per axis) to fill
  ~92% of the `0 0 1000 1400` viewBox and centered. Germany's real aspect
  ratio (taller north-south than wide east-west) is preserved rather than
  distorted to fit a differently-shaped box.
- **Simplification**: Douglas-Peucker (Ramer-Douglas-Peucker), applied in
  projected pixel space with tolerance `epsilon = 3.5px`, after splitting the
  closed ring into two open chains (plain RDP degenerates on a closed ring's
  zero-length start/end baseline). The mainland ring's raw 2,373 points
  simplify to 330 points. Output file: `data/geo/germany.json`, 4,986 bytes.
- **Regeneration**: `python3 tools/fetch_geo.py`. The ~14 MB source download
  is never committed — only the derived `germany.json` is. If the source is
  unreachable, the script raises and leaves the committed file untouched
  rather than writing a degraded one; this run did not need that path.
- **Only cities inside Germany's projected bounds belong in `CITY_COORDS`.**
  This projection is built to fit Germany's own bounding box
  (`build_projection`, above); it has no sensible answer for a point far
  outside it. A city outside Germany — Dash0's New York headquarters is the
  case that exposed this — projects to a coordinate thousands of units past
  the `0 0 1000 1400` viewBox, and an SVG clips anything outside its viewBox
  by default, so a bubble placed there simply doesn't render, on any city,
  every time.

  This was tried once: New York was added to `CITY_COORDS`, projected to
  `[-7972.4, 2357.3]`, and confirmed live (via `getComputedStyle` on the
  rendered `<svg>`, and by reading `.map__pin`'s actual `cx`/`cy` off the
  page) to be clipped to nothing. Worse, because `assets/js/map.js` used to
  treat "has an entry in this file" as the whole test for placeable, New York
  counted as `known` rather than `unplaced` — so it dropped out of the "Not
  shown on the map" note too, and the page gave no indication anywhere that
  Dash0 was missing. That was a regression on the honest fallback it
  replaced, and it has been reverted: New York is not in `CITY_COORDS`, and
  Dash0 is shown in the "Not shown on the map" note, same as any other HQ
  this map cannot place.

  `assets/js/map.js` now enforces the rule at render time as well as this
  file honouring it by convention: `renderMap` parses the live `viewBox` and
  treats a city as placeable only if its coordinates fall inside it, so an
  out-of-bounds entry — however it got into this file — is routed to the
  "Not shown" note exactly like a missing one, and cannot silently vanish a
  company's bubble again. See `docs/CANDIDATES.md`'s Dash0 note for the
  register-level reasoning (rule 1 is satisfied by founding, not HQ, so
  Dash0 stays in the register with a foreign HQ that this map, by design,
  cannot draw).
