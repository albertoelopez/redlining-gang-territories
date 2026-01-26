import re

# Read original full gang territories KML
with open('la_gang_territories.kml', 'r', encoding='utf-8') as f:
    content = f.read()

# Get header (everything before first Folder)
header_match = re.search(r'^(.*?)<Folder>', content, flags=re.DOTALL)
header = header_match.group(1) if header_match else ''

footer = '''  </Document>
</kml>'''

# Extract Compton & Lynwood folder
pattern = r'(<Folder>\s*<name><!\[CDATA\[Compton & Lynwood\]\]></name>.*?</Folder>)'
match = re.search(pattern, content, flags=re.DOTALL)

if match:
    folder = match.group(1)
    kml = header + folder + '\n' + footer
    with open('la_gangs_compton.kml', 'w', encoding='utf-8') as f:
        f.write(kml)
    print("Created: la_gangs_compton.kml")

    # Count placemarks
    pm_count = len(re.findall(r'<Placemark>', folder))
    print(f"Placemarks: {pm_count}")
else:
    print("Folder not found")
