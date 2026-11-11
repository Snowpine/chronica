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
    """the LOCALES, REGIONS, UNPUBLISHED regions and event TYPES that index.html knows"""
    html = open(f"{ROOT}/index.html", encoding="utf-8").read()
    locales = re.findall(r"(\w+): \[", re.search(r"const LOCALES = \{([^}]*)\}", html).group(1))
    regions = re.findall(r'"([\w-]+)"', re.search(r"const REGIONS = \[([^\]]*)\]", html).group(1))
    unpublished = re.findall(r'"([\w-]+)"', re.search(r"const UNPUBLISHED = \[([^\]]*)\]", html).group(1))
    types = re.findall(r"(\w+): \{ sym:", re.search(r"const TYPES = \{(.*?)\};", html, re.S).group(1))
    return locales, regions, unpublished, types


def check_shared(langs, regions):
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
        missing = [r for r in regions if len(loc.get("regions", {}).get(r, [])) != 2]
        if missing:
            errors.append(f"locales/{code}.json regions: no [name, subtitle] for {missing} (the region menu)")


def check_deploy(regions, unpublished):
    """an unpublished region must be left out of the deployment, and a region left out of it must be unpublished"""
    lines = [l.strip() for l in open(f"{ROOT}/.assetsignore", encoding="utf-8")]
    skipped = {m.group(1) for l in lines if (m := re.fullmatch(r"/regions/([\w-]+)/", l))}
    for rid in sorted(set(unpublished) - set(regions)):
        errors.append(f"index.html UNPUBLISHED: {rid!r} is not in REGIONS")
    for rid in sorted(set(unpublished) - skipped):
        errors.append(f".assetsignore: add /regions/{rid}/ (the region is unpublished in index.html, so it must not be deployed)")
    for rid in sorted(skipped - set(unpublished)):
        errors.append(f".assetsignore: /regions/{rid}/ is not deployed, but the live site would offer it (add it to UNPUBLISHED in index.html)")


def check_region(rid, langs, types):
    rdir = f"{ROOT}/regions/{rid}"
    where = f"regions/{rid}"
    rc = load(f"{rdir}/region.json")
    missing = [k for k in ("window", "projection", "focus", "start", "end", "eras", "scale", "lineages") if k not in rc]
    if missing:
        errors.append(f"{where}/region.json: no {missing}")
        return
    absent = [f"{name}.json" for name in ("borders", "events", "stories", "cities", "overviews") if not os.path.exists(f"{rdir}/{name}.json")]
    if absent:
        errors.append(f"{where}: missing {absent} (borders.json is built with scripts/make_data.py)")
        return
    borders = load(f"{rdir}/borders.json")
    years = borders["years"]
    y0, yn = years[0], rc["end"]
    if rc["eras"][0] > y0 or rc["eras"][-1] != yn:
        errors.append(f"{where}/region.json eras: should start by {y0} and end at {yn}")
    y0 = min(y0, rc["eras"][0])  # the timeline starts with the first era, which may come before the first snapshot
    if not (rc["scale"][0][0] <= y0 and rc["scale"][-1] == [yn, 1] and rc["scale"][0][1] == 0):
        errors.append(f"{where}/region.json scale: should run from [{y0} or earlier, 0] to [{yn}, 1]")
    # overviews.json: the main powers of a snapshot, by identity id, for the overview's buttons
    overviews = load(f"{rdir}/overviews.json")
    for k, ids in overviews.items():
        if not k.lstrip("-").isdigit() or int(k) not in years:
            errors.append(f"{where}/overviews.json: {k} is not a snapshot year")
            continue
        here = {(g.get("properties") or {}).get("i") for g in borders["topo"]["objects"][f"s{k}"]["geometries"]}
        gone = [i for i in ids if i not in here]
        if gone:
            errors.append(f"{where}/overviews.json {k}: {gone} are not on that snapshot")
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
    chart_names = set()
    for ch in stories:
        for r in ch.get("chart", []):
            if len(r) == 4 and isinstance(r[0], str) and all(isinstance(v, int) for v in r[1:]) and r[1] <= r[2] and r[3] >= 0:
                chart_names.add(r[0])
            else:
                errors.append(f"{where}/stories.json {ch['id']} chart: {r} should be [name key, from, to, lane]")
        for i, st in enumerate(ch["steps"]):
            for k in st.get("ev", []):
                if k not in event_keys:
                    errors.append(f"{where}/stories.json {ch['id']} step {i + 1}: unknown event {k!r}")
            for k in st.get("hl", []):
                if k not in idents and k not in lineages:
                    errors.append(f"{where}/stories.json {ch['id']} step {i + 1}: {k!r} is neither a state nor a lineage")

    # every name key the page may show
    names = {"_none"} | chart_names
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
        ov = sec("overviews")
        odd = sorted(k for k in ov if not k.lstrip("-").isdigit() or int(k) not in years)
        if odd:
            errors.append(f"{tag} overviews: {odd} are not snapshot years")
        odd = sorted(k for k, v in ov.items() if not (isinstance(v, list) and len(v) == 2 and all(isinstance(t, str) and t for t in v)))
        if odd:
            errors.append(f"{tag} overviews: {odd} should be [title, text]")
        if ov:  # once a region has overviews, a snapshot without one opens on a bare list of events
            missing = [y for y in years if str(y) not in ov]
            if missing:
                warnings.append(f"{tag} overviews: none for {missing}")
        prof = sec("profiles")
        odd = sorted(k for k, v in prof.items() if not (isinstance(v, list) and len(v) == 2 and isinstance(v[0], str) and isinstance(v[1], str) and v[1]))
        if odd:
            errors.append(f"{tag} profiles: {odd} should be [dates and capital, text]")
        odd = sorted(set(prof) - names)
        if odd:
            warnings.append(f"{tag} profiles: {odd} are not names on the map")
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
        about = loc.get("about")
        if about is None:
            warnings.append(f"{tag}: no about (the footer's Sources and notes link is hidden)")
        elif not (isinstance(about, list) and all(isinstance(s, dict) and isinstance(s.get("h"), str)
                                                  and all(isinstance(t, str) for t in s.get("p", []))
                                                  and all(isinstance(i, list) and 1 <= len(i) <= 2 for i in s.get("items", []))
                                                  for s in about)):
            errors.append(f"{tag} about: should be [{{\"h\": heading, \"p\": [paragraphs], \"items\": [[text, url?], ...]}}, ...]")
        known = {"names": None, "lineages": lineages, "events": set(event_keys), "stories": {c["id"] for c in stories}}
        for kind, table in sec("aliases").items():
            if kind not in known:
                errors.append(f"{tag} aliases: unknown group {kind!r}")
            elif known[kind] is not None:
                bad = sorted(set(table) - known[kind])
                if bad:
                    errors.append(f"{tag} aliases.{kind}: unknown keys {bad}")


def main():
    langs, page_regions, unpublished, types = page_lists()
    regions = sys.argv[1:] or sorted(d for d in os.listdir(f"{ROOT}/regions") if os.path.isfile(f"{ROOT}/regions/{d}/region.json"))
    check_shared(langs, page_regions)
    check_deploy(page_regions, unpublished)
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
