import re

with open('la_gang_territories.kml', 'r', encoding='utf-8') as f:
    content = f.read()

# Get header up to first folder
header_match = re.search(r'^(.*?)(\s*<Folder>)', content, flags=re.DOTALL)
header = header_match.group(1).rstrip() + '\n' if header_match else ''

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
            folder_content = match.group(1)
            placemarks = re.findall(r'(<Placemark>.*?</Placemark>)', folder_content, flags=re.DOTALL)
            return placemarks
    return []

def create_kml(name, folder_names, filename):
    all_placemarks = []
    for fn in folder_names:
        pms = get_placemarks_from_folder(content, fn)
        print(f"  {fn}: {len(pms)} placemarks")
        all_placemarks.extend(pms)

    kml = header
    kml += f'    <Folder>\n'
    kml += f'      <name>{name}</name>\n'
    for pm in all_placemarks:
        # Fix indentation
        kml += '      ' + pm.strip() + '\n'
    kml += '    </Folder>\n'
    kml += footer

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(kml)
    print(f"  -> {filename} ({len(all_placemarks)} total)\n")

print("1. Central & East LA:")
create_kml(
    "Central & East LA",
    ["Central & West Los Angeles", "Northeast, Southeast, & East Los Angeles"],
    "la_gangs_central_east_fixed.kml"
)

print("2. South Bay & Compton:")
create_kml(
    "South Bay & Compton",
    ["Inglewood & South Bay", "Compton & Lynwood"],
    "la_gangs_southbay_compton_fixed.kml"
)
