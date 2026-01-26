import re

# Read the South LA gang territories KML
with open('la_south_gang_territories.kml', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract all Placemarks from all folders
placemarks = re.findall(r'<Placemark>.*?</Placemark>', content, flags=re.DOTALL)
print(f"Found {len(placemarks)} placemarks")

# Extract styles from original file
styles_match = re.search(r'(<Style.*?</StyleMap>)\s*<Folder>', content, flags=re.DOTALL)
styles = styles_match.group(1) if styles_match else ''

# Create a new KML with all placemarks in a single folder
new_kml = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>South LA Gang Territories</name>
    <description>Gang territories in South Los Angeles, Inglewood, Compton, and Long Beach</description>
''' + styles + '''
    <Folder>
      <name>South LA Gang Territories</name>
'''

for pm in placemarks:
    new_kml += pm + '\n'

new_kml += '''    </Folder>
  </Document>
</kml>'''

with open('la_south_gangs_merged.kml', 'w', encoding='utf-8') as f:
    f.write(new_kml)

print("Created: la_south_gangs_merged.kml (single layer)")
