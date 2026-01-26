import re

# Read the Compton & Long Beach KML
with open('la_gangs_compton_lb.kml', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract all Placemarks
placemarks = re.findall(r'<Placemark>.*?</Placemark>', content, flags=re.DOTALL)
print(f"Found {len(placemarks)} placemarks")

# Get header (everything before first Folder)
header_match = re.search(r'^(.*?)<Folder>', content, flags=re.DOTALL)
header = header_match.group(1) if header_match else ''

# Create single folder KML
kml = header + '''    <Folder>
      <name>Compton & Long Beach</name>
'''
for pm in placemarks:
    kml += pm + '\n'
kml += '''    </Folder>
  </Document>
</kml>'''

with open('la_gangs_compton_lb_merged.kml', 'w', encoding='utf-8') as f:
    f.write(kml)
print("Created: la_gangs_compton_lb_merged.kml (1 layer)")
