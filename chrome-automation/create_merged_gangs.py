import re

# Read original full gang territories KML
with open('la_gang_territories.kml', 'r', encoding='utf-8') as f:
    content = f.read()

# Get header (everything before first Folder)
header_match = re.search(r'^(.*?)<Folder>', content, flags=re.DOTALL)
header = header_match.group(1) if header_match else ''

footer = '''  </Document>
</kml>'''

def extract_folder(content, folder_name):
    patterns = [
        rf'(<Folder>\s*<name>{re.escape(folder_name)}</name>.*?</Folder>)',
        rf'(<Folder>\s*<name><!\[CDATA\[{re.escape(folder_name)}\]\]></name>.*?</Folder>)'
    ]
    for pattern in patterns:
        match = re.search(pattern, content, flags=re.DOTALL)
        if match:
            return match.group(1)
    return None

def get_placemarks(folder_content):
    return re.findall(r'<Placemark>.*?</Placemark>', folder_content, flags=re.DOTALL)

def create_merged_kml(name, folders, filename):
    all_placemarks = []
    for folder_name in folders:
        folder = extract_folder(content, folder_name)
        if folder:
            pms = get_placemarks(folder)
            all_placemarks.extend(pms)
            print(f"  {folder_name}: {len(pms)} markers")

    kml = header + f'''    <Folder>
      <name>{name}</name>
'''
    for pm in all_placemarks:
        kml += pm + '\n'
    kml += '''    </Folder>
''' + footer

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(kml)
    print(f"  Created: {filename} ({len(all_placemarks)} total markers)\n")

def create_single_kml(folder_name, filename):
    folder = extract_folder(content, folder_name)
    if folder:
        pms = get_placemarks(folder)
        kml = header + folder + '\n' + footer
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(kml)
        print(f"  Created: {filename} ({len(pms)} markers)\n")
    else:
        print(f"  ERROR: Could not find folder '{folder_name}'\n")

print("Creating merged gang files...\n")

# Merge 1: Central & East LA
print("1. Central & East LA:")
create_merged_kml(
    "Central & East LA",
    ["Central & West Los Angeles", "Northeast, Southeast, & East Los Angeles"],
    "la_gangs_central_east.kml"
)

# Merge 2: South Los Angeles
print("2. South Los Angeles:")
create_merged_kml(
    "South Los Angeles",
    ["South Los Angeles (West Side)", "South Los Angeles (East Side)"],
    "la_gangs_south_la.kml"
)

# Merge 3: South Bay & Compton
print("3. South Bay & Compton:")
create_merged_kml(
    "South Bay & Compton",
    ["Inglewood & South Bay", "Compton & Lynwood"],
    "la_gangs_southbay_compton.kml"
)

# Single files for the 3 new areas
print("4. San Fernando Valley:")
create_single_kml("San Fernando Valley", "la_gangs_sfv.kml")

print("5. San Gabriel Valley & Inland Empire:")
create_single_kml("San Gabriel Valley & Inland Empire", "la_gangs_sgv.kml")

print("6. Long Beach & Harbor Area:")
create_single_kml("Long Beach & Harbor Area", "la_gangs_longbeach.kml")

print("Done! Created 6 KML files.")
