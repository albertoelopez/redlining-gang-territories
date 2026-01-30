# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a data visualization project studying correlations between historical HOLC redlining maps (1939) and modern gang territories in Los Angeles, Chicago, and Detroit. The project processes geospatial data (GeoJSON, KML) and automates imports into Google My Maps.

## Key Commands

### Chrome Automation Setup
```bash
cd chrome-automation
npm install
```

### Running Import Scripts
First start Chrome with remote debugging on Windows:
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="D:\ChromeDebug"
```

Then run Node.js automation scripts:
```bash
node import-kml.js           # Import redlining KML files
node import-remaining.js     # Import gang territory layers
```

### Python Data Processing
Scripts run from `chrome-automation/` directory:
```bash
python merge_all_grades.py      # Combine HOLC grades A-D into single KML
python create_merged_utf8.py    # Merge gang regions with UTF-8 encoding
python filter_la_gangs.py       # Filter LA gang data by region
```

## Architecture

### Data Flow
1. **Source data**: HOLC GeoJSON from Mapping Inequality, gang territory KML from Google Maps
2. **Processing**: Python scripts merge/filter KML files, apply styling
3. **Import**: Node.js + Puppeteer automates Google My Maps import via Chrome DevTools Protocol

### Chrome Automation (`chrome-automation/`)
- Uses `puppeteer-core` to connect to existing Chrome instance (port 9222)
- Navigates Google Picker iframe to upload KML files programmatically
- Scripts are specialized for different data sources (gangs, redlining, regions)

### Data Files
- Root level: GeoJSON files by city and HOLC grade (A-D)
- `chrome-automation/`: KML files with built-in styling for Google My Maps
- KML colors follow HOLC convention: Green (A), Blue (B), Yellow (C), Red (D)

## Important Constraints

- Google My Maps has a **10-layer limit** per map
- KML colors use ABGR format (not RGBA)
- Puppeteer connects to existing Chrome session, does not launch new browser
