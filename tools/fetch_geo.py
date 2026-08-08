"""Builds data/geo/germany.json: a simplified Germany outline plus a set of
city coordinates, both projected into the same 0-1000 x 0-1400 SVG viewBox
by a single projection function (project_point, below).

The site never fetches this at runtime — data/geo/germany.json is a small,
committed, derived artefact. This script does the one-time (or occasional
re-run) heavy lifting: downloading a ~14 MB public-domain GeoJSON source,
picking Germany's mainland polygon out of it, simplifying that polygon's
point count, and projecting everything into pixel space.

Source: https://github.com/datasets/geo-countries (data/countries.geojson),
itself derived from Natural Earth admin-0 boundaries (public domain). See
data/geo/README.md for full provenance.

Run: python3 tools/fetch_geo.py
"""
import json
import pathlib
import sys
import urllib.request

GEOJSON_URL = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
ISO3 = "DEU"
OUT_PATH = pathlib.Path("data/geo/germany.json")
README_PATH = pathlib.Path("data/geo/README.md")

VIEW_W, VIEW_H = 1000, 1400
MARGIN = 0.92          # fraction of the viewBox the projected outline should fill
SIMPLIFY_EPSILON = 3.5  # pixel-space Douglas-Peucker tolerance, post-projection

# lat, lon (matching how the task brief listed them) for every city the map
# should be able to place a bubble on. Projected with the same function as
# the outline, so a city bubble and the coastline can never drift apart.
CITY_COORDS = {
    "Berlin": (52.520, 13.405), "Munich": (48.137, 11.575), "Hamburg": (53.551, 9.994),
    "Frankfurt": (50.110, 8.682), "Cologne": (50.937, 6.960), "Düsseldorf": (51.227, 6.773),
    "Stuttgart": (48.776, 9.182), "Karlsruhe": (49.007, 8.404), "Leipzig": (51.340, 12.375),
    "Hanover": (52.376, 9.741), "Nuremberg": (49.452, 11.077), "Potsdam": (52.396, 13.059),
    "Dresden": (51.050, 13.738), "Bremen": (53.079, 8.802), "Aachen": (50.776, 6.084),
    "Heidelberg": (49.398, 8.672), "Münster": (51.960, 7.626), "Bonn": (50.735, 7.100),
    "Essen": (51.456, 7.012), "Mannheim": (49.487, 8.466),
    # A city missing from this dict does not break the map — map.js counts it
    # under "Not shown on the map" instead. That note is meant to be an honest
    # fallback for a genuinely unplaceable HQ, not a holding pen for cities
    # nobody got round to adding, so anything that turns up as a company's
    # hq.city belongs here. Freiburg (Black Forest Labs) and Chemnitz
    # (Staffbase) arrived with the second batch of records.
    "Freiburg": (47.999, 7.842), "Chemnitz": (50.828, 12.921),
}


def fetch_geojson(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def find_country(geojson, iso3):
    for feature in geojson["features"]:
        props = feature.get("properties", {})
        if props.get("ISO3166-1-Alpha-3") == iso3:
            return feature
    raise ValueError(f"no feature with ISO3166-1-Alpha-3 == {iso3!r} in source")


def ring_area(ring):
    """Shoelace formula on raw lon/lat — only used to rank polygons by size,
    so the degree-space (rather than true equal-area) approximation is fine."""
    area = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def polygons_from_geometry(geometry):
    """Yield each polygon's exterior ring (list of [lon, lat] pairs, first ==
    last) from a Polygon or MultiPolygon geometry. Interior rings (holes) are
    not relevant here — none of Germany's polygons in this source have any."""
    if geometry["type"] == "Polygon":
        yield geometry["coordinates"][0]
    elif geometry["type"] == "MultiPolygon":
        for polygon in geometry["coordinates"]:
            yield polygon[0]
    else:
        raise ValueError(f"unexpected geometry type {geometry['type']!r}")


def pick_mainland(geometry):
    rings = list(polygons_from_geometry(geometry))
    if not rings:
        raise ValueError("geometry has no rings at all")
    rings.sort(key=ring_area, reverse=True)
    mainland, dropped = rings[0], rings[1:]
    if len(mainland) < 4:  # a closed ring needs >= 3 distinct points + the closing point
        raise ValueError(f"largest ring has only {len(mainland)} points, too few to be real")
    return mainland, dropped


def build_projection(ring, margin=MARGIN):
    """One projection function, used for both the outline and the cities, so
    they can never disagree. Simple equirectangular projection: longitude is
    scaled by cos(mean latitude) so a degree of longitude and a degree of
    latitude cover comparable ground distance at Germany's latitude, then the
    whole thing is scaled uniformly (not stretched per-axis) to fit the
    viewBox — Germany's real aspect ratio (taller than wide) is preserved
    rather than distorted to fill a differently-shaped box.
    """
    lons = [lon for lon, lat in ring]
    lats = [lat for lon, lat in ring]
    lon_min, lon_max = min(lons), max(lons)
    lat_min, lat_max = min(lats), max(lats)
    lat_mid = (lat_min + lat_max) / 2
    import math
    cos_lat = math.cos(math.radians(lat_mid))

    width_raw = (lon_max - lon_min) * cos_lat
    height_raw = lat_max - lat_min
    scale = min(VIEW_W * margin / width_raw, VIEW_H * margin / height_raw)

    proj_width = width_raw * scale
    proj_height = height_raw * scale
    offset_x = (VIEW_W - proj_width) / 2
    offset_y = (VIEW_H - proj_height) / 2

    def project(lon, lat):
        x = (lon - lon_min) * cos_lat * scale + offset_x
        y = (lat_max - lat) * scale + offset_y  # north (high lat) -> small y
        return round(x, 1), round(y, 1)

    return project


def _perpendicular_distance(point, start, end):
    (px, py), (sx, sy), (ex, ey) = point, start, end
    dx, dy = ex - sx, ey - sy
    if dx == 0 and dy == 0:
        return ((px - sx) ** 2 + (py - sy) ** 2) ** 0.5
    t = ((px - sx) * dx + (py - sy) * dy) / (dx * dx + dy * dy)
    proj_x, proj_y = sx + t * dx, sy + t * dy
    return ((px - proj_x) ** 2 + (py - proj_y) ** 2) ** 0.5


def _rdp(points, epsilon):
    """Ramer-Douglas-Peucker on an open polyline (points[0] and points[-1]
    are kept unconditionally)."""
    if len(points) < 3:
        return points
    start, end = points[0], points[-1]
    max_dist, index = 0.0, 0
    for i in range(1, len(points) - 1):
        dist = _perpendicular_distance(points[i], start, end)
        if dist > max_dist:
            max_dist, index = dist, i
    if max_dist > epsilon:
        left = _rdp(points[: index + 1], epsilon)
        right = _rdp(points[index:], epsilon)
        return left[:-1] + right
    return [start, end]


def simplify_ring(points, epsilon):
    """Douglas-Peucker on a *closed* ring (points[0] == points[-1]). Plain RDP
    degenerates on a closed ring — its start/end baseline has zero length, so
    every point looks maximally distant from it. Split the ring at its two
    antipodal-ish points (index 0 and the midpoint) into two open chains,
    simplify each independently, then stitch the results back together."""
    unique = points[:-1]  # drop the duplicated closing point
    n = len(unique)
    mid = n // 2
    chain_a = unique[0: mid + 1]
    chain_b = unique[mid:] + unique[0:1]
    simplified_a = _rdp(chain_a, epsilon)
    simplified_b = _rdp(chain_b, epsilon)
    # simplified_a ends where simplified_b starts (unique[mid]); drop that
    # duplicate. simplified_b ends where simplified_a starts (unique[0]);
    # leave it off too since the SVG path closes with Z.
    return simplified_a[:-1] + simplified_b[:-1]


def path_from_ring(points):
    if not points:
        return ""
    commands = [f"M{points[0][0]},{points[0][1]}"]
    commands += [f"L{x},{y}" for x, y in points[1:]]
    commands.append("Z")
    return "".join(commands)


class GeoFetchError(Exception):
    """Raised when a real outline cannot be produced, at any of three
    distinguishable stages: the source couldn't be downloaded, the DEU
    feature wasn't found in it, or its geometry was unusable once found.

    main() reports whichever of those it is and exits non-zero *without*
    calling build()'s file-write step — a regeneration that can't produce a
    real outline must never overwrite the committed data/geo/germany.json
    with a degraded one. The old null-outline fallback silently did exactly
    that (same exit code either way), so a re-run during a network blip
    could quietly replace a good file and nothing would catch it before
    commit. Failing loudly and leaving the existing file untouched is the
    only safe default.
    """


def _download_mainland(source_url):
    try:
        geojson = fetch_geojson(source_url)
    except Exception as error:
        raise GeoFetchError(f"download failed: could not fetch {source_url} ({error})") from error

    try:
        feature = find_country(geojson, ISO3)
    except ValueError as error:
        raise GeoFetchError(f"DEU feature not found: {error}") from error

    try:
        mainland_lonlat, dropped_rings = pick_mainland(feature["geometry"])
    except (KeyError, ValueError) as error:
        raise GeoFetchError(f"geometry unusable: {error}") from error

    return mainland_lonlat, dropped_rings


def build(out_path=OUT_PATH, readme_path=README_PATH, source_url=GEOJSON_URL):
    """Raises GeoFetchError (and writes nothing) if a real outline can't be
    produced — see GeoFetchError's docstring for why there is no degraded
    fallback here any more."""
    mainland_lonlat, dropped_rings = _download_mainland(source_url)

    project = build_projection(mainland_lonlat)
    mainland_px = [project(lon, lat) for lon, lat in mainland_lonlat]
    simplified_px = simplify_ring(mainland_px, SIMPLIFY_EPSILON)
    outline_path = path_from_ring(simplified_px)

    # CITY_COORDS is keyed (lat, lon) to match how the brief listed them;
    # project() takes (lon, lat), so the pair is swapped here.
    cities_px = {name: list(project(lon, lat)) for name, (lat, lon) in CITY_COORDS.items()}

    dropped_points = sum(len(r) - 1 for r in dropped_rings)
    report = {
        "mainland_raw_points": len(mainland_lonlat) - 1,
        "mainland_simplified_points": len(simplified_px),
        "dropped_ring_count": len(dropped_rings),
        "dropped_point_count": dropped_points,
    }

    payload = {
        "viewBox": f"0 0 {VIEW_W} {VIEW_H}",
        "outline": outline_path,
        "cities": cities_px,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return payload, report


def main(source_url=None):
    """Returns a process exit code; does not itself call sys.exit so tests
    can invoke this directly (e.g. with a deliberately broken source_url)
    without spawning a subprocess."""
    try:
        _, report = build(source_url=source_url or GEOJSON_URL)
    except GeoFetchError as error:
        print(f"error: {error}", file=sys.stderr)
        print(f"Refusing to touch {OUT_PATH} — it is left exactly as it was.", file=sys.stderr)
        return 1
    size = OUT_PATH.stat().st_size
    print(f"Wrote {OUT_PATH} ({size:,} bytes): mainland ring "
          f"{report['mainland_raw_points']} -> {report['mainland_simplified_points']} points, "
          f"dropped {report['dropped_ring_count']} smaller rings "
          f"({report['dropped_point_count']} points total).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
