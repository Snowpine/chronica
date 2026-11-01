"""Build per-snapshot polity layers, snapshot-to-snapshot territory changes and summary series.

usage: build.py <region_dir> <clip_dir> <out_dir>
The region's polities.py says which polygons are the same state, which belong to a lineage and which source labels
are wrong; see regions/europe/polities.py.
"""
import json, math, os, sys
from collections import defaultdict
from shapely.geometry import shape, mapping as _mapping, MultiPolygon, Polygon, Point
from shapely.geometry.polygon import orient
from shapely.ops import unary_union, polylabel
from shapely.validation import make_valid

region_dir, clip_dir, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.abspath(region_dir))
import polities as P

YEARS, PEOPLES, UNNAMED, REASSIGN = P.YEARS, P.PEOPLES, P.UNNAMED, P.REASSIGN
LINEAGE_IDS = list(P.LINEAGE_NAMES)
LINEAGE_OF = {n: k for k, ns in P.LINEAGE_NAMES.items() for n in ns}
LINEAGE_OF.update(P.OVERLORD_LINEAGES)
IDENTITY_OF = {n: k for k, ns in P.IDENTITY_GROUPS.items() for n in ns}
MIN_CHANGE_KM2 = 6000
os.makedirs(out_dir, exist_ok=True)


def fix_props(p, year):
    """Return (name, overlord) after correcting known data issues."""
    name = (p.get("NAME") or "").strip()
    sub = (p.get("SUBJECTO") or "").strip()
    name = "" if name == "?" else name
    sub = "" if sub == "?" or sub.isdigit() else sub  # placeholders such as "1" and "3"
    sub = P.OVERLORD_RENAMES.get(sub, sub)
    if not name and sub:
        name = sub
    group = P.GROUP_RENAMES.get((p.get("PARTOF") or "").strip())
    if group:
        name, sub = group, ""
    fixed = next((n for test, n in P.RENAMES.get(name, []) if test(year)), None)
    if fixed:
        sub = sub if sub != name else fixed
        name = fixed
    if sub in ("", name) or sub == (p.get("PARTOF") or "").strip() == name:
        sub = ""
    return name or None, sub or None


def name_key(name, year):
    """Key under which a locale stores the display name of NAME in the given snapshot year."""
    for test, tag in P.VARIANTS.get(name, []):
        if test(year):
            return f"{name}|{tag}"
    return name


def polys(g):
    g = make_valid(g)
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, MultiPolygon):
        return [p for p in g.geoms if not p.is_empty]
    return [p for gg in getattr(g, "geoms", []) for p in polys(gg)]


def mapping(g):
    # d3-geo wants clockwise exterior rings
    ps = [orient(p, sign=-1.0) for p in polys(g)]
    return _mapping(ps[0] if len(ps) == 1 else MultiPolygon(ps))


def km2(g):
    return sum(p.area * math.cos(math.radians(p.centroid.y)) for p in polys(g)) * 111.32 ** 2


def label_pt(g):
    big = max(polys(g), key=lambda p: p.area)
    try:
        pt = polylabel(big, tolerance=0.05)
    except Exception:
        pt = big.representative_point()
    return round(pt.x, 2), round(pt.y, 2)


def outline(name, y):
    fs = json.load(open(f"{clip_dir}/c_{y}.geojson"))["features"]
    return make_valid(unary_union([shape(f["geometry"]) for f in fs if f.get("geometry") and fix_props(f["properties"], y)[0] == name]))


snap = {}  # year -> list of dicts
for y in YEARS:
    groups = defaultdict(list)
    meta = {}
    for f in json.load(open(f"{clip_dir}/c_{y}.geojson"))["features"]:
        if not f.get("geometry"):
            continue
        name, sub = fix_props(f["properties"], y)
        if name in P.NOT_POLITIES:
            continue
        geom = make_valid(shape(f["geometry"]))
        if not name:
            name = next((n for ys, pt, n in UNNAMED if y in ys and geom.contains(Point(*pt))), None)
        for ry, rname, to, from_y in REASSIGN:
            if ry == y and rname == name:
                region = outline(to, from_y)
                groups[to].extend(polys(geom.intersection(region)))
                meta.setdefault(to, None)
                geom = geom.difference(region)
        key = name or "_none"
        groups[key].extend(polys(geom))
        if key not in meta or sub:
            meta[key] = sub
    feats = []
    for key, ps in groups.items():
        g = make_valid(unary_union(ps))
        if g.is_empty:
            continue
        name = None if key == "_none" else key
        sub = meta[key]
        lin = LINEAGE_OF.get(name, "") if name else ""
        vassal = 0
        if name and not lin and sub and LINEAGE_OF.get(sub):
            lin, vassal = LINEAGE_OF[sub], 1
        lx, ly = label_pt(g)
        feat = {
            "geom": g,
            "i": IDENTITY_OF.get(name, name) if name else "_none",
            "n": name_key(name, y) if name else "_none",
            "l": lin, "v": vassal,
            "o": name_key(sub, y) if sub else "",
            "a": int(round(km2(g))),
            "x": lx, "y": ly,
        }
        if name in PEOPLES:
            feat["p"] = 1
        feats.append(feat)
    snap[y] = feats


def union_by_ident(feats):
    d = defaultdict(list)
    for f in feats:
        d[f["i"]].append(f["geom"])
    return {k: make_valid(unary_union(v)) for k, v in d.items()}


def key_of(feats, ident):
    c = [f for f in feats if f["i"] == ident]
    return max(c, key=lambda f: f["a"])["n"] if c else ""


peoples = {IDENTITY_OF.get(n, n) for n in PEOPLES}
changes = {}
for py, y in zip(YEARS, YEARS[1:]):
    prev, cur = union_by_ident(snap[py]), union_by_ident(snap[y])
    out = []
    for k, g in cur.items():
        if k == "_none" or k in peoples:
            continue
        gained = g.difference(prev[k]) if k in prev else g
        if gained.is_empty or km2(gained) < MIN_CHANGE_KM2:
            continue
        for j, pg in prev.items():
            if j == k or not pg.intersects(gained):
                continue
            piece = make_valid(gained.intersection(pg))
            piece = make_valid(piece.buffer(-0.05).buffer(0.05).intersection(gained))
            ps = [p for p in polys(piece) if km2(p) > 800]
            if not ps:
                continue
            piece = MultiPolygon(ps) if len(ps) > 1 else ps[0]
            a = km2(piece)
            if a < MIN_CHANGE_KM2:
                continue
            lx, ly = label_pt(piece)
            out.append({"geom": piece, "to": k, "toK": key_of(snap[y], k), "from": j,
                        "fromK": key_of(snap[py], j) if j != "_none" else "_none",
                        "a": int(round(a)), "x": lx, "y": ly})
    out.sort(key=lambda c: -c["a"])
    changes[y] = out

# series: lineage area per snapshot (incl. vassals), identity area per snapshot, and name runs
lin_series = {k: [0] * len(YEARS) for k in LINEAGE_IDS}
ident_series = defaultdict(lambda: [0] * len(YEARS))
ident_names = defaultdict(list)
ident_lin = {}
lin_names = defaultdict(list)
for idx, y in enumerate(YEARS):
    best_core = {}
    for f in snap[y]:
        if f["l"]:
            lin_series[f["l"]][idx] += f["a"]
            if not f["v"] and (f["l"] not in best_core or f["a"] > best_core[f["l"]]["a"]):
                best_core[f["l"]] = f
        if f["i"] == "_none":
            continue
        ident_series[f["i"]][idx] += f["a"]
        if f["l"] and not f["v"]:
            ident_lin[f["i"]] = f["l"]
        # a run of one name only continues through consecutive snapshots; a gap starts a new run
        names = ident_names[f["i"]]
        if names and names[-1][0] == f["n"] and names[-1][2] in (y, YEARS[idx - 1]):
            names[-1][2] = y
        else:
            names.append([f["n"], y, y])
    for l, f in best_core.items():
        rs = lin_names[l]
        if rs and rs[-1][0] == f["n"] and rs[-1][2] == YEARS[idx - 1]:
            rs[-1][2] = y
        else:
            rs.append([f["n"], y, y])

for y in YEARS:
    fc = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": mapping(f["geom"]),
         "properties": {k: v for k, v in f.items() if k != "geom"}} for f in snap[y]]}
    json.dump(fc, open(f"{out_dir}/s{y}.geojson", "w"), ensure_ascii=False)
    if y in changes:
        fc = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "geometry": mapping(c["geom"]),
             "properties": {"k": i}} for i, c in enumerate(changes[y])]}
        json.dump(fc, open(f"{out_dir}/d{y}.geojson", "w"), ensure_ascii=False)

meta = {
    "years": YEARS,
    "lineages": {k: {"names": lin_names.get(k, []), "s": lin_series[k]} for k in LINEAGE_IDS},
    "idents": {k: {"s": s, "names": ident_names[k], "l": ident_lin.get(k, ""), **({"p": 1} if k in peoples else {})}
               for k, s in ident_series.items()},
    "changes": {y: [{k: v for k, v in c.items() if k != "geom"} for c in cs] for y, cs in changes.items()},
}
json.dump(meta, open(f"{out_dir}/meta.json", "w"), ensure_ascii=False)

for y in YEARS[1:]:
    cs = changes[y]
    print(y, len(cs), "; ".join(f"{c['toK']}<-{c['fromK']} {c['a']//1000}k" for c in cs[:7]))
