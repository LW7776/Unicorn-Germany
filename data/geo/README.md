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
  simplify to 330 points. Output file: `data/geo/germany.json`, 4,866 bytes.
- **Regeneration**: `python3 tools/fetch_geo.py`. The ~14 MB source download
  is never committed — only the derived `germany.json` is. If the source is
  unreachable, the script raises and leaves the committed file untouched
  rather than writing a degraded one; this run did not need that path.
- **New York** (Dash0's `hq.city`) was added to `CITY_COORDS` and projected
  by the same `build_projection` as every other city, per its coordinates
  read from OpenStreetMap's Nominatim record (city=New York City,
  state=New York, country=USA: lat 40.7127281, lon -74.0060152). The result,
  confirmed both in this file and by reading `.map__pin`'s live `cx`/`cy` off
  the rendered page, is `[-7972.4, 2357.3]` — a long way outside the
  `0 0 1000 1400` viewBox, because this projection is fit to Germany's own
  bounding box and a point roughly 6,500 km to its west falls nowhere near
  it. This is a real, confirmed regression, not a hypothetical one:
  `assets/js/map.js` places a bubble for any city present in this file's
  `cities` object without checking it falls inside the viewBox, and the
  browser applies `overflow: hidden` to the map's `<svg>` (confirmed via
  `getComputedStyle` on the live page), which clips that bubble to nothing.
  Before this entry existed, Dash0 fell into `unplaced` and the page printed
  "Not shown on the map: New York (1)" — a visible, honest admission. Now it
  is `known` (New York has coordinates on file) but invisible, so the page
  renders **no note at all** and the company simply isn't on the map, with
  nothing telling a reader that. That is worse than the fallback it
  replaced. Left as-is pending a decision on how (or whether) the register
  should place a non-German HQ on a map of Germany at all; see
  `docs/CANDIDATES.md`'s Dash0 note.
