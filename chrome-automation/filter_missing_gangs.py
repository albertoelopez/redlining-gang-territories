import re

# Read original KML
with open('la_gang_territories.kml', 'r', encoding='utf-8') as f:
    content = f.read()

# Folders to KEEP (only the missing South LA areas)
folders_to_keep = [
    'South Los Angeles (West Side)',
    'Inglewood & South Bay',
    'South Los Angeles (East Side)',
    'Compton & Lynwood',
    'Long Beach & Harbor Area',
]

# Find all Folder blocks
folder_pattern = r'<Folder>\s*<name>(?:<!\[CDATA\[)?([^<\]]+)(?:\]\]>)?</name>.*?</Folder>'

def filter_folder(match):
    folder_name = match.group(1).strip()
    for keep_name in folders_to_keep:
        if keep_name in folder_name:
            print(f"Keeping: {folder_name}")
            return match.group(0)
    print(f"Removing: {folder_name}")
    return ''

# Keep only the folders we need
filtered = re.sub(folder_pattern, filter_folder, content, flags=re.DOTALL)

# Write filtered KML
with open('la_south_gang_territories.kml', 'w', encoding='utf-8') as f:
    f.write(filtered)

print("\nCreated: la_south_gang_territories.kml")
