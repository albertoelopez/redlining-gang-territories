import re

# Read original KML
with open('la_gang_territories.kml', 'r', encoding='utf-8') as f:
    content = f.read()

# Folders to REMOVE
folders_to_remove = [
    'Antelope Valley & Santa Clarita Valley',
    'San Fernando Valley',
    'San Gabriel Valley & Inland Empire',
]

# Find all Folder blocks
folder_pattern = r'<Folder>\s*<name>(?:<!\[CDATA\[)?([^<\]]+)(?:\]\]>)?</name>.*?</Folder>'

def should_keep_folder(match):
    folder_name = match.group(1).strip()
    for remove_name in folders_to_remove:
        if remove_name in folder_name:
            print(f"Removing: {folder_name}")
            return ''
    print(f"Keeping: {folder_name}")
    return match.group(0)

# Replace folders we want to remove with empty string
filtered = re.sub(folder_pattern, should_keep_folder, content, flags=re.DOTALL)

# Write filtered KML
with open('la_core_gang_territories.kml', 'w', encoding='utf-8') as f:
    f.write(filtered)

print("\nCreated: la_core_gang_territories.kml")
