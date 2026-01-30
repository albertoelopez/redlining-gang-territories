#!/usr/bin/env python3
"""
Extract HOLC redlining data for major US cities from the full HOLC GeoJSON file.
Outputs separate GeoJSON and KML files for each city.
"""

import json
import os

# Configuration
INPUT_FILE = "/mnt/d/AI_Projects/redlining_project/full_holc_data.json"
OUTPUT_DIR = "/mnt/d/AI_Projects/redlining_project"

# Cities to extract (must match names in the source data exactly)
CITIES = [
    "Chicago",
    "Detroit",
    "Philadelphia",
    "Cleveland",
    "St. Louis",
    "Baltimore",
    "Pittsburgh",
    "San Francisco",
    "New Orleans",
    "Atlanta"
]

# NYC boroughs to combine into "New York City"
NYC_BOROUGHS = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]

# HOLC grade colors in ABGR format (KML format)
# Grade A (Best) = Green, Grade B (Still Desirable) = Blue
# Grade C (Declining) = Yellow, Grade D (Hazardous) = Red
HOLC_COLORS = {
    "A": "7f00ff00",  # Green with 50% opacity
    "B": "7fff0000",  # Blue with 50% opacity
    "C": "7f00ffff",  # Yellow with 50% opacity
    "D": "7f0000ff",  # Red with 50% opacity
}

# Grade descriptions
GRADE_DESCRIPTIONS = {
    "A": "Best",
    "B": "Still Desirable",
    "C": "Declining",
    "D": "Hazardous"
}


def load_holc_data(filepath):
    """Load the full HOLC GeoJSON data."""
    print(f"Loading HOLC data from {filepath}...")
    with open(filepath, 'r') as f:
        data = json.load(f)
    print(f"Loaded {len(data['features'])} features")
    return data


def filter_features_by_city(features, city_name):
    """Filter features for a specific city."""
    return [f for f in features if f.get('properties', {}).get('city') == city_name]


def filter_features_by_cities(features, city_names):
    """Filter features for multiple cities (for NYC boroughs)."""
    return [f for f in features if f.get('properties', {}).get('city') in city_names]


def create_geojson(features, name):
    """Create a GeoJSON FeatureCollection."""
    return {
        "type": "FeatureCollection",
        "name": name,
        "features": features
    }


def save_geojson(geojson_data, filepath):
    """Save GeoJSON data to file."""
    with open(filepath, 'w') as f:
        json.dump(geojson_data, f)
    print(f"  Saved GeoJSON: {filepath}")


def get_coordinates_from_geometry(geometry):
    """Extract coordinate rings from various geometry types."""
    coords_list = []

    if geometry['type'] == 'Polygon':
        # For Polygon, outer ring is first element
        coords_list.append(geometry['coordinates'][0])
    elif geometry['type'] == 'MultiPolygon':
        # For MultiPolygon, each polygon's outer ring
        for polygon in geometry['coordinates']:
            coords_list.append(polygon[0])

    return coords_list


def format_coords_for_kml(coords):
    """Format coordinates for KML (lon,lat,alt format)."""
    return ' '.join([f"{c[0]},{c[1]},0" for c in coords])


def create_kml(features, name, year="1930s"):
    """Create KML document with HOLC styling."""

    # Build style definitions
    styles = ""
    for grade, color in HOLC_COLORS.items():
        styles += f'''    <Style id="grade{grade}Style">
      <PolyStyle>
        <color>{color}</color>
        <outline>1</outline>
      </PolyStyle>
      <LineStyle>
        <color>ff000000</color>
        <width>1</width>
      </LineStyle>
    </Style>
'''

    # Build placemarks
    placemarks = ""
    for feature in features:
        props = feature.get('properties', {})
        geometry = feature.get('geometry', {})

        grade = props.get('grade', 'D')
        # Clean up grade - strip whitespace, handle None
        if grade is None:
            grade = 'D'  # Default to D for unknown
        else:
            grade = grade.strip()
        area_id = props.get('label', props.get('name', 'Unknown'))
        grade_desc = props.get('category', GRADE_DESCRIPTIONS.get(grade, 'Unknown'))

        # Get all coordinate rings
        coord_rings = get_coordinates_from_geometry(geometry)

        for coords in coord_rings:
            coord_str = format_coords_for_kml(coords)

            placemarks += f'''    <Placemark>
      <name>{area_id}</name>
      <description>HOLC Grade: {grade} ({grade_desc})</description>
      <styleUrl>#grade{grade}Style</styleUrl>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>{coord_str}</coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
'''

    # Assemble KML document
    kml = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{name} - HOLC Redlining Map ({year})</name>
    <description>Home Owners' Loan Corporation (HOLC) "Residential Security" map for {name}</description>
{styles}{placemarks}  </Document>
</kml>'''

    return kml


def save_kml(kml_content, filepath):
    """Save KML content to file."""
    with open(filepath, 'w') as f:
        f.write(kml_content)
    print(f"  Saved KML: {filepath}")


def make_filename_safe(city_name):
    """Convert city name to safe filename."""
    return city_name.lower().replace(' ', '_').replace('.', '')


def process_city(features, city_name, output_name=None):
    """Process a single city or combined cities."""
    if output_name is None:
        output_name = city_name

    safe_name = make_filename_safe(output_name)

    print(f"\nProcessing {output_name}...")
    print(f"  Found {len(features)} features")

    if len(features) == 0:
        print(f"  WARNING: No features found for {output_name}")
        return False

    # Count by grade
    grade_counts = {}
    for f in features:
        grade = f.get('properties', {}).get('grade', 'Unknown')
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    print(f"  Grade distribution: {grade_counts}")

    # Save GeoJSON
    geojson_data = create_geojson(features, output_name)
    geojson_path = os.path.join(OUTPUT_DIR, f"{safe_name}_holc.geojson")
    save_geojson(geojson_data, geojson_path)

    # Save KML
    kml_content = create_kml(features, output_name)
    kml_path = os.path.join(OUTPUT_DIR, f"{safe_name}_holc.kml")
    save_kml(kml_content, kml_path)

    return True


def main():
    # Load data
    data = load_holc_data(INPUT_FILE)
    all_features = data['features']

    created_files = []

    # Process individual cities
    for city in CITIES:
        city_features = filter_features_by_city(all_features, city)
        if process_city(city_features, city):
            safe_name = make_filename_safe(city)
            created_files.append(f"{safe_name}_holc.geojson")
            created_files.append(f"{safe_name}_holc.kml")

    # Process NYC (combined boroughs)
    print("\n" + "="*50)
    print("Processing New York City (combined boroughs)...")
    nyc_features = filter_features_by_cities(all_features, NYC_BOROUGHS)

    # Show borough breakdown
    for borough in NYC_BOROUGHS:
        borough_features = filter_features_by_city(all_features, borough)
        print(f"  {borough}: {len(borough_features)} features")

    if process_city(nyc_features, NYC_BOROUGHS, "New York City"):
        created_files.append("new_york_city_holc.geojson")
        created_files.append("new_york_city_holc.kml")

    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Created {len(created_files)} files in {OUTPUT_DIR}:")
    for f in sorted(created_files):
        print(f"  - {f}")


if __name__ == "__main__":
    main()
