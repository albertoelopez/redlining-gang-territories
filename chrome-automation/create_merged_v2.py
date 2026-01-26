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

# Central & East LA - keep both original folders
print("Creating Central & East LA (keeping original folders)...")
folder1 = extract_folder(content, "Central & West Los Angeles")
folder2 = extract_folder(content, "Northeast, Southeast, & East Los Angeles")
if folder1 and folder2:
    kml = header + folder1 + '\n' + folder2 + '\n' + footer
    with open('la_gangs_central_east_v2.kml', 'w', encoding='utf-8') as f:
        f.write(kml)
    print("Created: la_gangs_central_east_v2.kml")

# South Bay & Compton - keep both original folders
print("\nCreating South Bay & Compton (keeping original folders)...")
folder3 = extract_folder(content, "Inglewood & South Bay")
folder4 = extract_folder(content, "Compton & Lynwood")
if folder3 and folder4:
    kml = header + folder3 + '\n' + folder4 + '\n' + footer
    with open('la_gangs_southbay_compton_v2.kml', 'w', encoding='utf-8') as f:
        f.write(kml)
    print("Created: la_gangs_southbay_compton_v2.kml")

print("\nDone!")
