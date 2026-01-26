import re

with open('la_gang_territories.kml', 'r', encoding='utf-8') as f:
    content = f.read()

header_match = re.search(r'^(.*?)<Folder>', content, flags=re.DOTALL)
header = header_match.group(1) if header_match else ''
footer = '''  </Document>
</kml>'''

def get_placemarks_from_folder(content, folder_name):
    patterns = [
        rf'<Folder>\s*<name>{re.escape(folder_name)}</name>(.*?)</Folder>',
        rf'<Folder>\s*<name><!\[CDATA\[{re.escape(folder_name)}\]\]></name>(.*?)</Folder>'
    ]
    for pattern in patterns:
        match = re.search(pattern, content, flags=re.DOTALL)
        if match:
            return re.findall(r'(<Placemark>.*?</Placemark>)', match.group(1), flags=re.DOTALL)
    return []

# Merge 1: Central & West + East LA
print("Creating: Central & East LA")
pms1 = get_placemarks_from_folder(content, "Central & West Los Angeles")
pms2 = get_placemarks_from_folder(content, "Northeast, Southeast, & East Los Angeles")
print(f"  Central & West: {len(pms1)}")
print(f"  East LA: {len(pms2)}")
all_pms = pms1 + pms2

kml1 = header + '''    <Folder>
      <name>Central & East LA</name>
'''
for pm in all_pms:
    kml1 += pm + '\n'
kml1 += '''    </Folder>
''' + footer

with open('la_gangs_central_east_v3.kml', 'w', encoding='utf-8') as f:
    f.write(kml1)
print(f"  Total: {len(all_pms)} -> la_gangs_central_east_v3.kml\n")

# Merge 2: Inglewood + Compton
print("Creating: Inglewood & Compton")
pms3 = get_placemarks_from_folder(content, "Inglewood & South Bay")
pms4 = get_placemarks_from_folder(content, "Compton & Lynwood")
print(f"  Inglewood: {len(pms3)}")
print(f"  Compton: {len(pms4)}")
all_pms2 = pms3 + pms4

kml2 = header + '''    <Folder>
      <name>Inglewood & Compton</name>
'''
for pm in all_pms2:
    kml2 += pm + '\n'
kml2 += '''    </Folder>
''' + footer

with open('la_gangs_inglewood_compton.kml', 'w', encoding='utf-8') as f:
    f.write(kml2)
print(f"  Total: {len(all_pms2)} -> la_gangs_inglewood_compton.kml")
