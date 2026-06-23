# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A data-visualization project studying the correlation between historical HOLC
redlining maps (1935–1940) and modern gang territories across 12 major US
cities: Los Angeles, Chicago, Detroit, Philadelphia, Cleveland, St. Louis,
Baltimore, Pittsburgh, San Francisco, New Orleans, Atlanta, and New York City.
It extracts/processes geospatial data (GeoJSON, KML) and automates publishing
one Google My Map per city via Chrome DevTools Protocol.

There is no build or test suite — this is a data pipeline plus browser
automation scripts.

## Data Pipeline (end to end)

The canonical flow is three stages. Stage 1–2 are Python; stage 3 is Node +
Puppeteer.

1. **Extract HOLC data** — `python chrome-automation/extract_major_cities.py`
   Reads `full_holc_data.json` (the complete ~239-city Mapping Inequality
   dataset, 10 MB) and writes `{city}_holc.geojson` + `{city}_holc.kml` to the
   repo root for each city. NYC is special-cased: its five boroughs (Manhattan,
   Brooklyn, Queens, Bronx, Staten Island) are merged into one `new_york_city`
   output. City names in the `CITIES` list must match the `properties.city`
   field in the source data exactly.

2. **Download gang territories** — `python chrome-automation/download_gang_maps.py`
   Fetches each city's gang KML from public Google My Maps via the
   `https://www.google.com/maps/d/kml?mid=<MID>&forcekml=1` endpoint, writing to
   `gang_territories/{city}_gangs.kml`. The `GANG_MAPS` dict maps city → map ID;
   source map IDs are also documented in `README.md`.

3. **Publish to Google My Maps** — `node chrome-automation/create-city-maps.js`
   (see Chrome Automation below). Imports the HOLC layer + gang layer into a new
   Google My Map per city and writes results to `map_urls.json`.

### Quantitative analysis (separate from publishing)

`python analyze_overlap.py` (repo root) measures the actual redlining↔gang
correlation: for each city it intersects the gang KML against the HOLC GeoJSON
grades and writes `analysis.csv` + a printed summary. Two metrics, because gang
data is uneven — **area overlap** where the gang map has polygons, **point-in-
polygon** where it's only markers (Chicago is points-only). The headline figure
is the Grade-D *disproportionality ratio*: gang D-share **conditional on the
HOLC-mapped footprint** ÷ the city's baseline D-share (>1 = over-represented in
redlined zones). Conditioning on the mapped footprint matters — HOLC only mapped
select neighborhoods, so raw "% of gang area in D" is diluted by area outside any
graded zone. Requires `shapely` + `lxml` (no geopandas/pyproj here, so KML is
parsed by hand and area uses a local equirectangular projection about the city
centroid — fine for within-city ratios).

## Chrome Automation

`create-city-maps.js` is the current/primary automation entry point. The many
older `import-*.js` and per-city/per-grade Python scripts
(`merge_all_grades.py`, `filter_la_gangs.py`, `extract_compton.py`, etc.) are
**superseded LA/Chicago/Detroit-era one-offs** kept for reference — prefer the
pipeline above unless reproducing that specific early work.

### Setup
```bash
cd chrome-automation
npm install
```

### Start Chrome with remote debugging (Windows, before running any Node script)
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="D:\ChromeDebug"
```
Then log into Google in that Chrome window. `node test-connection.js` verifies
the connection.

### Create maps
```bash
node create-city-maps.js --all          # all 11 cities in the CITIES array
node create-city-maps.js chicago        # a single city
```

### How it works
- Uses `puppeteer-core` to **connect to the already-running Chrome** (it never
  launches a browser). It tries `http://127.0.0.1:9222` then the WSL2 host IP
  `http://172.23.160.1:9222` — this repo is developed from WSL2 driving Chrome
  on the Windows host, hence the dual URLs and Windows-style `D:\` paths in the
  scripts (`PROJECT_ROOT = 'D:\\AI_Projects\\redlining_project'`).
- Drives the Google My Maps UI by walking the DOM text (`clickByText` via a
  `TreeWalker`) rather than stable selectors, then uploads KML through the
  **Google Picker iframe**'s `input[type=file]`. This is inherently fragile to
  Google UI changes; the `sleep()` delays and multi-fallback iframe lookup in
  `uploadKMLFile` exist to absorb that.

### MCP server (`index.js`)
`index.js` is a separate, standalone Model Context Protocol server
(`chrome-automation-mcp`, the `package.json` `start`/bin entry) exposing generic
Chrome-automation tools (`connect_to_chrome`, etc.) over stdio. It is **not**
part of the city-map pipeline — don't confuse it with `create-city-maps.js`.

## KML conventions

- **Colors are ABGR**, not RGBA (KML convention). HOLC grade palette used by
  `extract_major_cities.py`: A=Green `7f00ff00`, B=Blue `7fff0000`,
  C=Yellow `7f00ffff`, D=Red `7f0000ff` (`7f` = ~50% opacity). Note older
  scripts use slightly different blues (e.g. `merge_all_grades.py` uses
  `7fff9000`); match whichever file you're editing.
- HOLC grade meaning: **A "Best" (green), B "Still Desirable" (blue),
  C "Declining" (yellow), D "Hazardous"/redlined (red)**. Grade D is the
  historically redlined category.

## Constraints / gotchas

- Google My Maps allows **10 layers per map**; each city map uses 2 (HOLC +
  gangs), so there's headroom but don't fan out per-grade layers.
- Google My Maps also rejects KML imports **over ~5 MB**. St. Louis has no
  published map because its gang KML exceeds this — its data files exist but it
  is intentionally absent from `create-city-maps.js`'s `CITIES` array and from
  the README map table.
- `.gitignore` in `chrome-automation/` excludes `node_modules`, screenshots
  (`*.png`), `*.kmz`, and regenerable LA intermediate KMLs, while
  force-keeping the three source gang KMLs (`la_/chicago_/detroit_gang_territories.kml`).
