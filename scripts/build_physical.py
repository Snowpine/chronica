"""Build the faint rivers / lakes / mountain-range layer from Natural Earth (public domain).

usage: build_physical.py <region_dir> <natural_earth_geojson_dir> <out_dir>
needs ne_10m_rivers_lake_centerlines, ne_50m_lakes, ne_10m_geography_regions_polys (.geojson);
which rivers and ranges to keep and label comes from the region's physical.py
"""
import json, os, sys
from shapely.geometry import shape, mapping, box, LineString, MultiLineString, Polygon, MultiPolygon
from shapely.geometry.polygon import orient
from shapely.ops import linemerge, polylabel, unary_union
from shapely.validation import make_valid

region_dir, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.abspath(region_dir))
from physical import RIVERS, EXTRA, RANGES, RIVER_LABEL_BOX

(w, so), (e, n) = json.load(open(f"{region_dir}/region.json"))["window"]
BBOX = box(w, so, e, n)
CORE = box(*RIVER_LABEL_BOX)
NAME_TO_RIVER = {n: key for key, ns in RIVERS.items() for n in ns}
os.makedirs(out, exist_ok=True)
load = lambda n: json.load(open(f"{src}/{n}.geojson"))["features"]


def lines(g):
    if isinstance(g, LineString):
        return [g]
    if isinstance(g, MultiLineString):
        return list(g.geoms)
    return [p for gg in getattr(g, "geoms", []) for p in lines(gg)]


def polys(g):
    g = make_valid(g)
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, MultiPolygon):
        return list(g.geoms)
    return [p for gg in getattr(g, "geoms", []) for p in polys(gg)]


def poly_mapping(g):
    ps = [orient(p, sign=-1.0) for p in polys(g) if not p.is_empty]  # d3-geo wants clockwise exterior rings
    return mapping(ps[0] if len(ps) == 1 else MultiPolygon(ps))


rivers, by_label = [], {}
for f in load("ne_10m_rivers_lake_centerlines"):
    p, g = f["properties"], f["geometry"] and shape(f["geometry"])
    if not g or not g.intersects(BBOX):
        continue
    name, rank = p.get("name") or "", p.get("scalerank") or 99
    if rank > 7 and name not in EXTRA:
        continue
    g = g.intersection(BBOX)
    rivers.append({"type": "Feature", "geometry": mapping(g), "properties": {"r": min(rank, 9)}})
    key = NAME_TO_RIVER.get(name)
    if key:
        by_label.setdefault(key, [min(rank, 9), []])
        by_label[key][0] = min(by_label[key][0], rank)
        by_label[key][1].extend(lines(g))

river_labels = []
for key, (rank, ls) in by_label.items():
    merged = lines(linemerge(ls))
    inside = [l.intersection(CORE) for l in merged]
    cands = [l for g in inside for l in lines(g) if l.length > .8] or [l for l in merged if l.length > .5]
    if not cands:
        continue
    line = max(cands, key=lambda l: l.length)
    a, b = line.interpolate(.46, normalized=True), line.interpolate(.54, normalized=True)
    river_labels.append([key, round(a.x, 2), round(a.y, 2), round(b.x, 2), round(b.y, 2), int(rank)])

lakes = []
for f in load("ne_50m_lakes"):
    g = shape(f["geometry"])
    if g.intersects(BBOX) and g.area > .02:
        lakes.append({"type": "Feature", "geometry": poly_mapping(g.intersection(BBOX)), "properties": {}})

ranges, range_labels = [], []
for f in load("ne_10m_geography_regions_polys"):
    p = f["properties"]
    if p.get("FEATURECLA") != "Range/mtn" or p.get("NAME") not in RANGES:
        continue
    g = make_valid(shape(f["geometry"]))
    if not g.intersects(BBOX):
        continue
    g = unary_union(polys(g.intersection(BBOX)))
    ranges.append({"type": "Feature", "geometry": poly_mapping(g), "properties": {}})
    key, rank = RANGES[p["NAME"]]
    if key:
        pt = polylabel(max(polys(g), key=lambda q: q.area), tolerance=.05)
        range_labels.append([key, round(pt.x, 2), round(pt.y, 2), rank])

for name, feats in (("rivers", rivers), ("lakes", lakes), ("ranges", ranges)):
    json.dump({"type": "FeatureCollection", "features": feats}, open(f"{out}/{name}.geojson", "w"))
json.dump({"riverLabels": river_labels, "rangeLabels": range_labels}, open(f"{out}/labels.json", "w"))
print(f"rivers {len(rivers)}, lakes {len(lakes)}, ranges {len(ranges)}, river labels {len(river_labels)}, range labels {len(range_labels)}")
