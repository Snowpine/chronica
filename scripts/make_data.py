"""Rebuild a region's borders.json or physical.json from the raw sources in one go.

usage:
  python scripts/make_data.py <region> borders  <historical-basemaps>/geojson     [out.json]
  python scripts/make_data.py <region> physical <natural-earth-vector>/geojson    [out.json]

<region> is a folder under regions/ (e.g. europe). Its region.json gives the map window the sources are clipped to;
its polities.py and physical.py say how to read them. The output goes to regions/<region>/ unless out.json is given.
Needs Python 3 with shapely 2, and mapshaper (npm install -g mapshaper, or set MAPSHAPER=/path/to/mapshaper).
Intermediate files go to ./work/<region>, or to $WORK.
"""
import glob, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def source_file(y):
    """historical-basemaps file name of a snapshot year; negative years are BC (-500 is world_bc500.geojson)"""
    return f"world_bc{-y}.geojson" if y < 0 else f"world_{y}.geojson"


def mapshaper(*args):
    exe = os.environ.get("MAPSHAPER") or shutil.which("mapshaper")
    if not exe:
        sys.exit("mapshaper not found: npm install -g mapshaper, or set MAPSHAPER=/path/to/mapshaper")
    subprocess.run([exe, *args, "-quiet"], check=True)


def write(meta, topo_path, out):
    meta["topo"] = json.load(open(topo_path))
    with open(out, "w") as f:
        f.write(json.dumps(meta, ensure_ascii=False, separators=(",", ":")))
    print(f"wrote {out} ({os.path.getsize(out) // 1024} KB)")


def borders(region, src, out, work):
    sys.path.insert(0, region)
    from polities import YEARS
    (w, s), (e, n) = json.load(open(f"{region}/region.json"))["window"]
    clip, build = f"{work}/clip", f"{work}/build"
    os.makedirs(clip, exist_ok=True)
    for y in YEARS:
        mapshaper("-i", f"{src}/{source_file(y)}", "-clean", "-clip", f"bbox={w},{s},{e},{n}", "-simplify", "12%",
                  "keep-shapes", "-filter-slivers", "min-area=200km2", "-o", f"{clip}/c_{y}.geojson", "precision=0.001")
    shutil.rmtree(build, ignore_errors=True)
    subprocess.run([sys.executable, f"{HERE}/build.py", region, clip, build], check=True)
    layers = sorted(glob.glob(f"{build}/s*.geojson")) + sorted(glob.glob(f"{build}/d*.geojson"))
    mapshaper("-i", *layers, "combine-files", "-o", f"{work}/topo.json", "format=topojson", "quantization=60000")
    write(json.load(open(f"{build}/meta.json")), f"{work}/topo.json", out)


def physical(region, src, out, work):
    phys = f"{work}/phys"
    shutil.rmtree(phys, ignore_errors=True)
    subprocess.run([sys.executable, f"{HERE}/build_physical.py", region, src, phys], check=True)
    mapshaper("-i", f"{phys}/rivers.geojson", f"{phys}/lakes.geojson", f"{phys}/ranges.geojson", "combine-files",
              "-simplify", "25%", "keep-shapes", "-o", f"{phys}/topo.json", "format=topojson", "quantization=50000")
    write(json.load(open(f"{phys}/labels.json")), f"{phys}/topo.json", out)


if __name__ == "__main__":
    if len(sys.argv) not in (4, 5) or sys.argv[2] not in ("borders", "physical"):
        sys.exit(__doc__)
    name, what, src = sys.argv[1:4]
    region = f"{ROOT}/regions/{name}"
    if not os.path.isfile(f"{region}/region.json"):
        sys.exit(f"no region {name!r}: {region}/region.json not found")
    out = sys.argv[4] if len(sys.argv) == 5 else f"{region}/{what}.json"
    work = os.environ.get("WORK", f"{ROOT}/work/{name}")
    (borders if what == "borders" else physical)(region, src, out, work)
