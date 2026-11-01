# Chronica · 寰宇古今

[中文说明](README.zh.md)

Chronica is a historical atlas built region by region. The first region is *Europe Through the Ages* (欧陆古今), which covers Europe from 700 BC to AD 2000: 44 border snapshots, the territory that changed hands between each pair of them, 296 events and 10 story chapters. Every story step has a short lead plus a full text written for reading at length. The interface and all content are available in English and Chinese.

The page code itself is region-neutral: everything specific to a region lives in its folder under `regions/`, so another region (East Asia, the Middle East, …) can be added next to Europe without changing the page's code.

## What it does

- **Explore**: drag the timeline or press play to watch borders change. Hatched areas mark this snapshot's territorial changes. Click a state to see its name history and an area chart. Click a coloured lane (the "Powers" button left of the timeline opens them) to follow a lineage such as France or Russia across renamings.
- **Story**: chapters such as *The Century of Athens* or *The Age of Napoleon*, each a sequence of steps that moves the map. "Read in full" opens the reading view: the chapter on the right, the map on the left following the section you are reading.
- **Compare**: two years side by side with a draggable divider, the largest gains and losses, and the events in between.
- **Search** (`/`): states, lineages, cities (also under their former names), events and stories, including common nicknames such as *HRE*, *WWII*, 神罗, 一战.
- **Links**: the address always reflects the view, so any view can be shared (see [Links](#links)).

## Running it locally

The page reads its data with `fetch`, so it needs a local web server rather than opening the file directly. From any directory:

```bash
python3 path/to/chronica/scripts/serve.py
```

Then open http://localhost:8000 and press Ctrl+C to stop. If port 8000 is in use, pass another one: `serve.py 8001`.

## Language

The page picks its language in this order:

1. `?lang=<code>` in the address, e.g. `http://localhost:8000/?lang=zh`;
2. the language last chosen with the language button (stored in the browser);
3. the first of the browser's preferred languages that the atlas has (any `zh-*` counts as Chinese);
4. English.

The language button in the top right cycles through the languages listed in `LOCALES` in `index.html`.

## Project layout

```
chronica/
  index.html                 the page and all of its code; neither region- nor language-specific
  locales/
    en.json  zh.json         interface text (buttons, labels, help), shared by every region
  regions/
    europe/
      region.json            map window, projection, opening view and year, eras, time scale, lineage colours, compare presets
      borders.json           border snapshots (TopoJSON), territorial changes, area series     — built
      physical.json          rivers, lakes, mountain ranges                                     — built
      events.json            events: [key, year, latitude, longitude, type]
      stories.json           story chapters: per step a year, a map box, highlighted states, events
      cities.json            cities: [latitude, longitude, rank, [[from year, name key], …]]
      locales/
        en.json  zh.json     the region's content: names, eras, events, stories, search aliases
      polities.py            how to read the border source: snapshots, lineages, corrections
      physical.py            which rivers and mountain ranges to draw and label
  scripts/
    make_data.py             rebuilds a region's borders.json or physical.json from the sources
    build.py                 step of make_data.py: merges polities, computes changes and series
    build_physical.py        step of make_data.py: picks rivers, lakes and ranges
    check.py                 checks regions and locales for gaps
    serve.py                 local preview server
  LICENSE                    GPL-3.0
```

Years are integers throughout, negative for BC (`-500` is 500 BC); there is no year 0.

## region.json

| Field | Meaning |
|---|---|
| `window` | `[[west, south], [east, north]]` in degrees. The sources are clipped to it, and it is the area of sea drawn behind the land. |
| `projection` | A [d3-geo](https://d3js.org/d3-geo) projection name without the `geo` prefix, plus settings to call on it, e.g. `{"type": "ConicConformal", "parallels": [40, 62], "rotate": [-15, 0]}`. |
| `focus` | Points the opening view must contain; the map fits the smallest view around them. |
| `core` | Optional `[[west, south], [east, north]]`. Territorial changes inside it are listed before those at the edges of the window. Defaults to `window`. |
| `start`, `end` | The opening year, and the year the timeline ends. The timeline starts at the first border snapshot. |
| `eras` | Era boundaries, from the first snapshot year to `end`; the locales name the eras in between. |
| `scale` | The timeline's time scale: `[year, share]` pairs from `[first year, 0]` to `[end, 1]`, linear in between. Give sparse periods a smaller share. |
| `denseFrom` | Optional. Before this year, "recent events" reach back 100 years instead of 25, and the timeline counts events per half-century instead of per decade. |
| `lineages` | `{id: [light colour, dark colour]}` for each lineage in `polities.py`, in the order of the timeline lanes. |
| `presets` | Optional `[[left year, right year], …]` shortcuts in compare mode; the locales label them. |

## Locales

The page combines two files per language: `locales/<lang>.json`, which holds the interface text, and `regions/<id>/locales/<lang>.json`, which holds the region's content. Each section of the region file is laid over the matching section of the interface file, so the region's `ui` section adds the region's `title`, `subtitle` and `map` (the map's accessible name) to the interface text.

**Interface file** (`locales/<lang>.json`):

- `meta`:
  - `code`: the language code;
  - `lang`: a BCP 47 tag such as `fr`;
  - `name`: the language's own name, e.g. `Français`;
  - `area`: the area format (`number` groups digits the local way; `wan` counts in units of 10,000 for Chinese).
- `ui`: interface text.
  - Keep placeholders such as `{y}` and `{name}`.
  - A few entries (`keys`, `credit`, `changeRow`) contain HTML or have HTML inserted; keep their structure.
  - `bc` is how BC years are written, e.g. `{y} BC`, `前{y}`.
- `types`: names of the event types `war`, `treaty`, `politics`, `faith`, `culture` and `plague`. A new type also needs a map symbol in `TYPES` in `index.html`.

**Region file** (`regions/<id>/locales/<lang>.json`):

- `ui`: `title`, `subtitle`, `map`.
- `eras`: one name per era in `region.json`.
- `lanes`: short names for the timeline lanes. A `/` separates alternatives; narrow screens show the last one.
- `lineages`: full names of the lineages.
- `notes`: remarks on individual snapshots, keyed by year.
- `presets`: labels for the compare presets, keyed `"<left>-<right>"`.
- `names`, `cities`, `rivers`, `ranges`: place names, keyed by name key (see below).
- `short` (optional): shorter map labels used when a full name doesn't fit, e.g. `Polish–Lithuanian Commonwealth` → `Poland–Lithuania`. A trailing parenthesis such as "(France)" is dropped automatically and needs no entry.
- `events`: `{event key: [title, description]}`.
- `stories`: `{chapter id: {title, lede, steps: [[title, lead, full text?], …]}}`. The steps must match `stories.json` in number. The full text is optional and has the form `{"p": [paragraph, …], "facts": [[label, value], …]}`. A chapter that has full text on any step gets "Read in full" and the reading view. All 10 chapters of Europe have it: three paragraphs per step, about 260 words in English.
- `aliases` (optional): other names search should recognise, e.g. `HRE`, `WWII`, 神罗, 沙俄. There are four groups:
  - `names`, keyed by polity name key;
  - `lineages`, keyed by lineage id;
  - `events`, keyed by event key;
  - `stories`, keyed by chapter id.

  Each entry is a list of strings. English aliases also work in other languages. A result found through an alias shows the alias under its name, so a theme word such as "Industrial Revolution" can be attached to a representative event.

### Name keys

Polity names in `borders.json` are keys, not text in any language:

- Usually a key is the source's `NAME`, e.g. `Tsardom of Muscovy` or `Holy Roman Empire`.
- A name that should read differently in some years gets `|tag`, e.g. `Germany|empire` (up to 1914), `Germany|weimar` or `Germany|nazi`. The rules are in `VARIANTS` in the region's `polities.py`.
- `_none` stands for land with no recorded polity.

To show a name, the page looks up `names[key]` in the locale, then the key without its `|tag`. If both are missing it shows the source's English name, so a missing translation never breaks anything.

Ancient snapshots include many peoples and archaeological cultures (Celts, Urnfield cultures, …). These are not states, and the source often maps them in one snapshot and not the next. `PEOPLES` in `polities.py` lists them. The map draws them pale with italic labels, their spread is not counted as a territorial change, and compare mode leaves them out of gains and losses.

### Fallbacks

- A missing interface string shows its key.
- A missing polity, river or mountain name shows the source's English name.
- A region that has no file for the current language shows its English content inside the translated interface.

`scripts/check.py` reports all of these gaps.

## Adding a language

1. Copy `locales/en.json` to `locales/<code>.json` (e.g. `fr.json`) and translate `meta`, `ui` and `types`.
2. For each region, copy `regions/<id>/locales/en.json` to `<code>.json` and translate it. Until you do, that region shows English content.
3. Add the language to `LOCALES` in `index.html`: `fr: ["Français", "fr"]` (its own name and its BCP 47 tag).
4. Typography: the page CSS defaults to Chinese typography, and every other language gets a Latin display face and tighter letter spacing (the `:root:not([lang|="zh"])` rules). A language in another script, such as Japanese or Arabic, needs its own `:root[lang|="xx"]` rules there.
5. Run `python3 scripts/check.py` and fix what it reports.

## Adding a region

1. **Choose the window and the snapshots.** Pick a `window` and the [historical-basemaps](https://github.com/aourednik/historical-basemaps) years to use. Create `regions/<id>/region.json` as described above, using Europe's as a template.
2. **Describe the sources.** Copy `regions/europe/polities.py` and `physical.py` into the new folder and rewrite their tables. Every table must exist, but it may be empty.
   - `polities.py`:
     - `YEARS`: the snapshots;
     - `LINEAGE_NAMES`: polity names grouped into lineages; the ids must match `lineages` in `region.json`;
     - `OVERLORD_LINEAGES`: overlord spellings that differ from a lineage member's name;
     - `IDENTITY_GROUPS`: names that count as the same state, so a rename is not a territorial change;
     - corrections to source labels: `RENAMES`, `GROUP_RENAMES`, `OVERLORD_RENAMES`, `NOT_POLITIES`;
     - `PEOPLES`, `VARIANTS`;
     - geometry fixes: `UNNAMED`, `REASSIGN`.
   - `physical.py`: rivers and ranges to draw and label, by their Natural Earth names.
3. **Build the data** (see [Rebuilding the data](#rebuilding-the-data)):
   ```bash
   python3 scripts/make_data.py <id> borders  <historical-basemaps>/geojson
   ```
   ```bash
   python3 scripts/make_data.py <id> physical <natural-earth-vector>/geojson
   ```
   The build prints the largest changes in each snapshot. Implausible ones usually mean a source label needs a correction in `polities.py`.
4. **Write the content.** Add `events.json`, `stories.json` and `cities.json` (each may start as `[]`), then `locales/en.json` with at least `ui`, `eras`, `lanes` and `lineages`. Add other languages when ready.
5. **List the region.** Add its id to `REGIONS` in `index.html` and open `http://localhost:8000/?region=<id>`. The first region in the list is the default. There is no region menu yet; add one when there is a second region.
6. **Check it.** Run `python3 scripts/check.py <id>`. It lists untranslated names, story steps that don't match, unknown event keys, lineage mismatches and other problems.

## Links

The part of the address after `#` follows the current view:

- **Explore:**
  - `#1650`, `#500bc`: a year (BC written as `bc`).
  - `#1914/state:Serbia`, `#1650/lineage:poland`, `#1215/event:magna-carta`: a year with a state, lineage or event selected (keys as in the region's data).
- **Story:**
  - `#napoleon`, `#napoleon/3`: a chapter, at a given step.
  - `#napoleon/3/read`: the same step in the reading view.
  - `#stories`: the chapter list.
- **Compare:** `#compare-1914-1920`: two years side by side, optionally followed by `/state:…` and the like.

Query parameters go before the `#`: `?lang=en`, `?region=europe`.

## Rebuilding the data

You need Python 3 with shapely 2, and [mapshaper](https://github.com/mbloch/mapshaper) (`npm install -g mapshaper`, or point the `MAPSHAPER` environment variable at it). One command per file clips, merges, computes changes and packs the result. Intermediate files go to `work/<region>/`.

```bash
python3 scripts/make_data.py europe borders  <historical-basemaps>/geojson
```

```bash
python3 scripts/make_data.py europe physical <natural-earth-vector>/geojson
```

### Borders: `borders.json`

The source is the `geojson/world_<year>.geojson` files of https://github.com/aourednik/historical-basemaps (`world_bc<year>.geojson` for BC). `make_data.py borders`:

1. **Clips and simplifies** each snapshot listed in `YEARS` to the region's `window`, using mapshaper.
2. **Runs `scripts/build.py`** with the region's `polities.py`, which:
   - merges polygons of the same polity and assigns name keys, lineages and overlords;
   - corrects known source errors (`RENAMES`, `OVERLORD_RENAMES`, `UNNAMED`, `REASSIGN`);
   - computes the territory each state gained from each neighbour between consecutive snapshots, ignoring pieces under 6,000 km²;
   - builds per-state and per-lineage area series.
3. **Packs** all snapshots and changes into one TopoJSON file, together with that metadata.

New name keys need entries in each locale's `names`; without them the map shows the source's English names. `scripts/check.py` lists them.

### Rivers, lakes and mountains: `physical.json`

The source is [Natural Earth](https://www.naturalearthdata.com/) (public domain), from the `geojson/` folder of https://github.com/nvkelso/natural-earth-vector:

- `ne_10m_rivers_lake_centerlines`;
- `ne_50m_lakes`;
- `ne_10m_geography_regions_polys`.

`make_data.py physical` runs `scripts/build_physical.py` with the region's `physical.py`, which keeps the listed rivers and ranges and every lake in the window, then simplifies and packs the result.

## Sources and licence

The project, code and data alike, is released under [GPL-3.0](LICENSE).

- Borders: [aourednik/historical-basemaps](https://github.com/aourednik/historical-basemaps), GPL-3.0. `borders.json` is derived from it.
- Rivers, lakes and mountains: [Natural Earth](https://www.naturalearthdata.com/), public domain.
- Events, stories and translations were written for this project.
