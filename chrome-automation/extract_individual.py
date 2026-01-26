import re

with open('la_gang_territories.kml', 'r', encoding='utf-8') as f:
    content = f.read()

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

regions = [
    ("Central & West Los Angeles", "la_gangs_central_west.kml"),
    ("Northeast, Southeast, & East Los Angeles", "la_gangs_east_la.kml"),
    ("Inglewood & South Bay", "la_gangs_inglewood.kml"),
    ("Compton & Lynwood", "la_gangs_compton.kml"),
]

for name, filename in regions:
    folder = extract_folder(content, name)
    if folder:
        pms = len(re.findall(r'<Placemark>', folder))
        kml = header + folder + '\n' + footer
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(kml)
        print(f"{name}: {pms} markers -> {filename}")
