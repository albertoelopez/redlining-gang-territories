import re

# Read original full gang territories KML
with open('la_gang_territories.kml', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract styles
styles_match = re.search(r'(<Style.*?</StyleMap>)\s*<Folder>', content, flags=re.DOTALL)
styles = styles_match.group(1) if styles_match else ''

# Function to extract placemarks from a specific folder
def get_placemarks_from_folder(content, folder_name):
    # Find the folder
    pattern = rf'<Folder>\s*<name>(?:<!\[CDATA\[)?{re.escape(folder_name)}(?:\]\]>)?</name>.*?</Folder>'
    folder_match = re.search(pattern, content, flags=re.DOTALL)
    if folder_match:
        folder_content = folder_match.group(0)
        placemarks = re.findall(r'<Placemark>.*?</Placemark>', folder_content, flags=re.DOTALL)
        return placemarks
    return []

# Group 1: Inglewood & South Bay + South Los Angeles (East Side)
group1_placemarks = []
group1_placemarks.extend(get_placemarks_from_folder(content, 'Inglewood & South Bay'))
group1_placemarks.extend(get_placemarks_from_folder(content, 'South Los Angeles (East Side)'))
print(f"Group 1 (Inglewood + South LA East): {len(group1_placemarks)} placemarks")

# Group 2: Compton & Lynwood + Long Beach & Harbor Area
group2_placemarks = []
group2_placemarks.extend(get_placemarks_from_folder(content, 'Compton & Lynwood'))
group2_placemarks.extend(get_placemarks_from_folder(content, 'Long Beach & Harbor Area'))
print(f"Group 2 (Compton + Long Beach): {len(group2_placemarks)} placemarks")

# Create KML for Group 1
kml1 = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Inglewood & South LA East Gang Territories</name>
''' + styles + '''
    <Folder>
      <name>Inglewood & South LA East</name>
'''
for pm in group1_placemarks:
    kml1 += pm + '\n'
kml1 += '''    </Folder>
  </Document>
</kml>'''

with open('la_gangs_group1.kml', 'w', encoding='utf-8') as f:
    f.write(kml1)
print("Created: la_gangs_group1.kml")

# Create KML for Group 2
kml2 = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Compton & Long Beach Gang Territories</name>
''' + styles + '''
    <Folder>
      <name>Compton & Long Beach</name>
'''
for pm in group2_placemarks:
    kml2 += pm + '\n'
kml2 += '''    </Folder>
  </Document>
</kml>'''

with open('la_gangs_group2.kml', 'w', encoding='utf-8') as f:
    f.write(kml2)
print("Created: la_gangs_group2.kml")
