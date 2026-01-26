# Redlining & Gang Territories Mapping Project

A study of the correlation between historical HOLC redlining maps (1939) and modern gang territories in major US cities.

## Live Maps

- **Los Angeles**: [View Map](https://www.google.com/maps/d/edit?mid=1f9kXu7qkxzbTnd1BbzxK6VN-nZc1J8M&usp=sharing)

## Background

The Home Owners' Loan Corporation (HOLC) created "Residential Security" maps in the 1930s that graded neighborhoods:

- **Grade A (Green)** - "Best" - typically affluent, white neighborhoods
- **Grade B (Blue)** - "Still Desirable"
- **Grade C (Yellow)** - "Declining"
- **Grade D (Red)** - "Hazardous" - typically minority neighborhoods, denied loans

This practice, known as "redlining," systematically denied mortgage loans and investment to minority communities, creating concentrated poverty that persists today.

## Data Sources

- **Redlining Data**: [Mapping Inequality](https://dsl.richmond.edu/panorama/redlining/map#loc=3/41.2448/-105.4688) - University of Richmond
- **Gang Territory Maps**: Various Google My Maps sources

## Cities Covered

- Los Angeles, CA
- Chicago, IL
- Detroit, MI

## Chrome Automation Tools

The `chrome-automation/` folder contains tools for automating Google My Maps imports:

### Setup

```bash
cd chrome-automation
npm install
```

### Usage

1. Start Chrome with remote debugging:
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="D:\ChromeDebug"
```

2. Open your Google My Maps in that Chrome window

3. Run import scripts:
```cmd
node import-kml.js          # Import redlining KML files
node import-remaining.js    # Import gang territory layers
```

### Python Scripts

- `create_merged_utf8.py` - Merge gang territory regions with proper UTF-8 encoding
- `filter_la_gangs.py` - Filter LA gang data by region
- `merge_all_grades.py` - Combine HOLC grades into single layer

## Project Structure

```
redlining_project/
├── chrome-automation/       # Automation scripts
│   ├── *.js                # Node.js import scripts
│   ├── *.py                # Python data processing
│   └── *.kml               # KML data files
├── *_grade_*.geojson       # HOLC data by grade
└── README.md
```

## Layer Limits

Google My Maps has a 10-layer limit per map. For comprehensive coverage:
- Use 4 layers for HOLC grades (A, B, C, D)
- Merge gang territory regions to fit remaining slots
- Or create separate maps per city

## License

Data sources retain their original licenses. This project is for educational purposes.
