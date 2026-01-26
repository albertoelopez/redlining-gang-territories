import re

# Read original full gang territories KML
with open('la_gang_territories.kml', 'r', encoding='utf-8') as f:
    content = f.read()

# Get header (everything before first Folder)
header_match = re.search(r'^(.*?)<Folder>', content, flags=re.DOTALL)
header = header_match.group(1) if header_match else ''

# Get footer
footer = '''  </Document>
</kml>'''

# Function to extract a complete folder
def extract_folder(content, folder_name):
    # Handle both plain names and CDATA wrapped names
    patterns = [
        rf'(<Folder>\s*<name>{re.escape(folder_name)}</name>.*?</Folder>)',
        rf'(<Folder>\s*<name><!\[CDATA\[{re.escape(folder_name)}\]\]></name>.*?</Folder>)'
    ]
    for pattern in patterns:
        match = re.search(pattern, content, flags=re.DOTALL)
        if match:
            return match.group(1)
    return None

# Extract folders for Group 1
folder1 = extract_folder(content, 'Inglewood & South Bay')
folder2 = extract_folder(content, 'South Los Angeles (East Side)')

if folder1 and folder2:
    kml1 = header + folder1 + '\n' + folder2 + '\n' + footer
    with open('la_gangs_inglewood_south.kml', 'w', encoding='utf-8') as f:
        f.write(kml1)
    print(f"Created: la_gangs_inglewood_south.kml")
else:
    print(f"Folder1 found: {folder1 is not None}, Folder2 found: {folder2 is not None}")

# Extract folders for Group 2
folder3 = extract_folder(content, 'Compton & Lynwood')
folder4 = extract_folder(content, 'Long Beach & Harbor Area')

if folder3 and folder4:
    kml2 = header + folder3 + '\n' + folder4 + '\n' + footer
    with open('la_gangs_compton_lb.kml', 'w', encoding='utf-8') as f:
        f.write(kml2)
    print(f"Created: la_gangs_compton_lb.kml")
else:
    print(f"Folder3 found: {folder3 is not None}, Folder4 found: {folder4 is not None}")
