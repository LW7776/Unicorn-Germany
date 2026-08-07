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
  unreachable, the script falls back to writing `outline: null` (bubbles
  still render, just without a coastline); this run did not need that path.
