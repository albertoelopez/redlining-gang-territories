# Redlining & Gang Territories Mapping Project

A study of the correlation between historical HOLC redlining maps (1935-1940) and modern gang territories in major US cities.

## Live Maps

- **Los Angeles**: [View Map](https://www.google.com/maps/d/edit?mid=1f9kXu7qkxzbTnd1BbzxK6VN-nZc1J8M&usp=sharing)

## Background

The Home Owners' Loan Corporation (HOLC) created "Residential Security" maps in the 1930s that graded neighborhoods:

- **Grade A (Green)** - "Best" - typically affluent, white neighborhoods
- **Grade B (Blue)** - "Still Desirable"
- **Grade C (Yellow)** - "Declining"
- **Grade D (Red)** - "Hazardous" - typically minority neighborhoods, denied loans

This practice, known as "redlining," systematically denied mortgage loans and investment to minority communities, creating concentrated poverty that persists today.

## Cities Covered

| City | HOLC Areas | Gang Data |
|------|------------|-----------|
| Los Angeles, CA | 417 | ✓ |
| Chicago, IL | 703 | ✓ |
| Detroit, MI | 239 | ✓ |
| Philadelphia, PA | 83 | ✓ |
| Cleveland, OH | 192 | ✓ |
| St. Louis, MO | 127 | ✓ |
| Baltimore, MD | 60 | ✓ |
| Pittsburgh, PA | 116 | ✓ |
| San Francisco, CA | 98 | ✓ |
| New Orleans, LA | 136 | ✓ |
| Atlanta, GA | 113 | ✓ |
| New York City, NY | 403 | ✓ |

## Data Sources

### Redlining Data
- [Mapping Inequality](https://dsl.richmond.edu/panorama/redlining/map) - University of Richmond

### Gang Territory Maps
| City | Source |
|------|--------|
| Los Angeles | [Gangs of Los Angeles](https://www.google.com/maps/d/u/0/viewer?mid=1ul5yqMj7_JgM5xpfOn5gtlO-bTk) |
| Chicago | [GangMap.com / r/Chiraqology](https://www.google.com/maps/d/viewer?mid=1xe7X8O0tiDRdJUNqG8IHEkcYaqyQOSs) |
| Detroit | [GangMap.com](https://www.google.com/maps/d/viewer?mid=1CqZGEDsnlpF0z7TZy8oGtxHo0q9uqNg) |
| Philadelphia | [Philly.Wiki](https://www.google.com/maps/d/viewer?mid=170j6JIjSRYraeh1xGf-auKlR6HnRuBo) |
| Cleveland | [r/StraightFromThaOH](https://www.google.com/maps/d/viewer?mid=1a3vq_epf5x8xi_Ja8OvUqWaWb7PUkas) |
| St. Louis | [GangMap.com](https://www.google.com/maps/d/viewer?mid=1BlP8dWqpsrwljeqkQGarSa57mbzJfq0) |
| Baltimore | [GangMap.com](https://www.google.com/maps/d/viewer?mid=1mpCVI7qXDuOes-4utDr2FK3HSsMbzRM) |
| Pittsburgh | [Community Map](https://www.google.com/maps/d/viewer?mid=1as3Dn6-Ecu69l66mU-5ifD0ycZk) |
| San Francisco | [OSINT Archives](https://www.google.com/maps/d/viewer?mid=1PD1YdFZWhv_-1o6ZulmPoLMkQAM) |
| New Orleans | [GangMap.com](https://www.google.com/maps/d/viewer?mid=1zeodrS0XnUt8IximIS9-pmx7OR8Dl8A) |
| Atlanta | [GangMap.com](https://www.google.com/maps/d/viewer?mid=1hMEvQwd1n9Jccxsy-1LzhwozIXkzpz8) |
| New York City | [GangMap.com](https://www.google.com/maps/d/viewer?mid=1CMk3O2D9HcjSdc8W5mepDj30JENpR48f) |

## Project Structure

```
redlining_project/
├── chrome-automation/           # Automation scripts
│   ├── create-city-maps.js     # Create Google My Maps per city
│   ├── download_gang_maps.py   # Download gang territory KMLs
│   ├── extract_major_cities.py # Extract HOLC data by city
│   └── *.js, *.py              # Other processing scripts
├── gang_territories/            # Gang territory KML files
│   └── {city}_gangs.kml
├── {city}_holc.geojson          # HOLC data per city (GeoJSON)
├── {city}_holc.kml              # HOLC data per city (KML with styling)
├── full_holc_data.json          # Complete HOLC dataset (all 239 cities)
└── README.md
```

## Chrome Automation Tools

### Setup

```bash
cd chrome-automation
npm install
```

### Creating City Maps

1. Start Chrome with remote debugging:
```cmd
"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="D:\ChromeDebug"
```

2. Log into Google in that Chrome window

3. Run the map creator:
```cmd
node create-city-maps.js --all          # Create all city maps
node create-city-maps.js chicago        # Create single city map
```

### Data Processing Scripts

```bash
# Extract HOLC data for major cities from full dataset
python extract_major_cities.py

# Download gang territory KMLs from Google My Maps
python download_gang_maps.py
```

## Layer Limits

Google My Maps has a 10-layer limit per map. Each city map uses:
- 1 layer for HOLC redlining (all grades combined)
- 1 layer for gang territories

## License

Data sources retain their original licenses. This project is for educational and research purposes.
