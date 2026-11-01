"""Check regions and locales for gaps: missing translations, unknown keys, story steps out of step, bad references.

usage: python scripts/check.py [region ...]     (default: every folder under regions/)

Errors make the page show raw keys or break a feature; warnings are gaps it covers with a fallback (a polity, river or
mountain name missing from a locale shows the source's English name; a region missing a language shows English).
Exits with status 1 if there are errors.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load = lambda p: json.load(open(p, encoding="utf-8"))
errors, warnings = [], []


def page_lists():
    """the LOCALES, REGIONS and event TYPES that index.html knows"""
    html = open(f"{ROOT}/index.html", encoding="utf-8").read()
    locales = re.findall(r"(\w+): \[", re.search(r"const LOCALES = \{([^}]*)\}", html).group(1))
    regions = re.findall(r'"([\w-]+)"', re.search(r"const REGIONS = \[([^\]]*)\]", html).group(1))
    types = re.findall(r"(\w+): \{ sym:", re.search(r"const TYPES = \{(.*?)\};", html, re.S).group(1))
    return locales, regions, types


def check_shared(langs):
    base = load(f"{ROOT}/locales/en.json")
    for code in langs:
        path = f"{ROOT}/locales/{code}.json"
        if not os.path.exists(path):
            errors.append(f"locales/{code}.json: missing (index.html lists {code} in LOCALES)")
            continue
        loc = load(path)
        if loc.get("meta", {}).get("code") != code:
            errors.append(f"locales/{code}.json: meta.code should be {code!r}")
        for section in ("ui", "types"):
            missing = set(base[section]) - set(loc.get(section, {}))
            if missing:
                errors.append(f"locales/{code}.json {section}: missing {sorted(missing)}")


def check_region(rid, langs, types):
    rdir = f"{ROOT}/regions/{rid}"
    where = f"regions/{rid}"
    rc = load(f"{rdir}/region.json")
    missing = [k for k in ("window", "projection", "focus", "start", "end", "eras", "scale", "lineages") if k not in rc]
    if missing:
        errors.append(f"{where}/region.json: no {missing}")
        return
    absent = [f"{name}.json" for name in ("borders", "events", "stories", "cities") if not os.path.exists(f"{rdir}/{name}.json")]
    if absent:
        errors.append(f"{where}: missing {absent} (borders.json is built with scripts/make_data.py)")
        return
    borders = load(f"{rdir}/borders.json")
    years = borders["years"]
    y0, yn = years[0], rc["end"]
    if not (rc["scale"][0][0] <= y0 and rc["scale"][-1] == [yn, 1] and rc["scale"][0][1] == 0):
        errors.append(f"{where}/region.json scale: should run from [{y0} or earlier, 0] to [{yn}, 1]")
    if rc["eras"][0] > y0 or rc["eras"][-1] != yn:
        errors.append(f"{where}/region.json eras: should start by {y0} and end at {yn}")
    periods = rc.get("periods", [])
    if periods and (periods[0] != rc["eras"][0] or periods[-1] != rc["eras"][-1] or not set(periods) <= set(rc["eras"])):
        errors.append(f"{where}/region.json periods: should run from the first to the last era boundary, using only era boundaries")
    if not y0 <= rc["start"] <= yn:
        errors.append(f"{where}/region.json start: {rc['start']} is outside {y0}..{yn}")
    if set(rc["lineages"]) != set(borders["lineages"]):
        errors.append(f"{where}: lineages differ between region.json {sorted(rc['lineages'])} "
                      f"and borders.json (polities.py) {sorted(borders['lineages'])}")
    for a, b in rc.get("presets", []):
        if not (y0 <= a <= yn and y0 <= b <= yn):
            errors.append(f"{where}/region.json presets: {a}-{b} is outside {y0}..{yn}")

    events = load(f"{rdir}/events.json")
    stories = load(f"{rdir}/stories.json")
    cities = load(f"{rdir}/cities.json")
    phys = load(f"{rdir}/physical.json") if os.path.exists(f"{rdir}/physical.json") else None
    event_keys = [e[0] for e in events]
    for key, y, lat, lon, kind in events:
        if kind not in types:
            errors.append(f"{where}/events.json {key}: type {kind!r} is not one of the page's TYPES {types}")
        if not y0 <= y <= yn:
            warnings.append(f"{where}/events.json {key}: year {y} is outside the timeline {y0}..{yn}")
    dupes = {k for k in event_keys if event_keys.count(k) > 1}
    if dupes:
        errors.append(f"{where}/events.json: duplicate keys {sorted(dupes)}")
    idents, lineages = set(borders["idents"]), set(borders["lineages"])
    for ch in stories:
        for i, st in enumerate(ch["steps"]):
            for k in st.get("ev", []):
                if k not in event_keys:
                    errors.append(f"{where}/stories.json {ch['id']} step {i + 1}: unknown event {k!r}")
            for k in st.get("hl", []):
                if k not in idents and k not in lineages:
                    errors.append(f"{where}/stories.json {ch['id']} step {i + 1}: {k!r} is neither a state nor a lineage")

    # every name key the page may show
    names = {"_none"}
    for y in years:
        for g in borders["topo"]["objects"][f"s{y}"]["geometries"]:
            p = g.get("properties") or {}
            names.update(k for k in (p.get("n"), p.get("o")) if k)
    for info in list(borders["idents"].values()) + list(borders["lineages"].values()):
        names.update(r[0] for r in info["names"])
    city_keys = {k for c in cities for _, k in c[3] if k}
    rivers = {r[0] for r in phys["riverLabels"]} if phys else set()
    ranges = {r[0] for r in phys["rangeLabels"]} if phys else set()

    for code in langs:
        path = f"{rdir}/locales/{code}.json"
        tag = f"{where}/locales/{code}.json"
        if not os.path.exists(path):
            (errors if code == "en" else warnings).append(f"{tag}: missing; the page shows this region's English content")
            continue
        loc = load(path)
        sec = lambda k: loc.get(k) or {}
        for k in ("title", "subtitle", "map"):
            if k not in sec("ui"):
                errors.append(f"{tag} ui: no {k!r}")
        if len(loc.get("eras", [])) != len(rc["eras"]) - 1:
            errors.append(f"{tag} eras: {len(loc.get('eras', []))} names for {len(rc['eras']) - 1} eras")
        if loc.get("erasShort") and len(loc["erasShort"]) != len(rc["eras"]) - 1:
            errors.append(f"{tag} erasShort: {len(loc['erasShort'])} names for {len(rc['eras']) - 1} eras")
        if len(loc.get("periods", [])) != max(0, len(periods) - 1):
            errors.append(f"{tag} periods: {len(loc.get('periods', []))} names for {max(0, len(periods) - 1)} periods")
        for k in ("lanes", "lineages"):
            missing = lineages - set(sec(k))
            if missing:
                errors.append(f"{tag} {k}: missing {sorted(missing)}")
        missing = [k for k in event_keys if k not in sec("events")]
        if missing:
            errors.append(f"{tag} events: {len(missing)} missing, e.g. {missing[:5]}")
        extra = set(sec("events")) - set(event_keys)
        if extra:
            warnings.append(f"{tag} events: {len(extra)} not in events.json, e.g. {sorted(extra)[:5]}")
        for ch in stories:
            tx = sec("stories").get(ch["id"])
            if not tx:
                errors.append(f"{tag} stories: no {ch['id']!r}")
                continue
            if len(tx.get("steps", [])) != len(ch["steps"]):
                errors.append(f"{tag} stories.{ch['id']}: {len(tx.get('steps', []))} steps, stories.json has {len(ch['steps'])}")
            for i, st in enumerate(tx.get("steps", [])):
                long = st[2] if len(st) > 2 else None
                if long is not None and not (isinstance(long.get("p"), list) and all(len(f) == 2 for f in long.get("facts", []))):
                    errors.append(f"{tag} stories.{ch['id']} step {i + 1}: full text should be {{\"p\": [...], \"facts\": [[k, v], ...]}}")
        odd = sorted(k for k in sec("notes") if not k.lstrip("-").isdigit() or int(k) not in years)
        if odd:
            warnings.append(f"{tag} notes: {odd} are not snapshot years")
        for a, b in rc.get("presets", []):
            if f"{a}-{b}" not in sec("presets"):
                warnings.append(f"{tag} presets: no label for {a}-{b}")
        missing = sorted(k for k in city_keys if k not in sec("cities"))
        if missing:
            errors.append(f"{tag} cities: missing {missing}")
        missing = sorted(k for k in names if k not in sec("names") and k.split("|")[0] not in sec("names"))
        if missing:
            warnings.append(f"{tag} names: {len(missing)} polity names untranslated, e.g. {missing[:5]}")
        for k, keys in (("rivers", rivers), ("ranges", ranges)):
            missing = sorted(keys - set(sec(k)))
            if missing:
                warnings.append(f"{tag} {k}: missing {missing}")
        known = {"names": None, "lineages": lineages, "events": set(event_keys), "stories": {c["id"] for c in stories}}
        for kind, table in sec("aliases").items():
            if kind not in known:
                errors.append(f"{tag} aliases: unknown group {kind!r}")
            elif known[kind] is not None:
                bad = sorted(set(table) - known[kind])
                if bad:
                    errors.append(f"{tag} aliases.{kind}: unknown keys {bad}")


def main():
    langs, page_regions, types = page_lists()
    regions = sys.argv[1:] or sorted(d for d in os.listdir(f"{ROOT}/regions") if os.path.isfile(f"{ROOT}/regions/{d}/region.json"))
    check_shared(langs)
    for rid in regions:
        if rid not in page_regions:
            warnings.append(f"regions/{rid}: not listed in REGIONS in index.html")
        check_region(rid, langs, types)
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("error:", e)
    print(f"checked {', '.join(regions)} in {', '.join(langs)}: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
