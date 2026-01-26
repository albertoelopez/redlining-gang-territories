import re

# Read all grade files and extract placemarks with their styles
grades = ['A', 'B', 'C', 'D']
colors = {
    'A': '7f00ff00',  # Green
    'B': '7fff9000',  # Blue
    'C': '7f00ffff',  # Yellow
    'D': '7f0000ff',  # Red
}
grade_names = {
    'A': 'Best',
    'B': 'Desirable',
    'C': 'Declining',
    'D': 'Redlined',
}

all_placemarks = []

for grade in grades:
    filename = f'los_angeles_grade_{grade}.kml'
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract placemarks
    placemarks = re.findall(r'<Placemark>.*?</Placemark>', content, flags=re.DOTALL)
    print(f"Grade {grade}: {len(placemarks)} areas")

    # Update placemark names to include grade
    for pm in placemarks:
        # Extract name
        name_match = re.search(r'<name>(.*?)</name>', pm)
        if name_match:
            old_name = name_match.group(1)
            new_name = f"{old_name} (Grade {grade})"
            pm = pm.replace(f'<name>{old_name}</name>', f'<name>{new_name}</name>')

        # Update style reference to use the grade-specific style
        pm = re.sub(r'<styleUrl>.*?</styleUrl>', f'<styleUrl>#grade{grade}Style</styleUrl>', pm)
        all_placemarks.append(pm)

print(f"\nTotal: {len(all_placemarks)} areas")

# Create combined KML
kml = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>LA HOLC Grades (1939)</name>
    <description>All HOLC redlining grades for Los Angeles - A (Best/Green), B (Desirable/Blue), C (Declining/Yellow), D (Redlined/Red)</description>
    <Style id="gradeAStyle">
      <PolyStyle>
        <color>7f00ff00</color>
        <outline>1</outline>
      </PolyStyle>
      <LineStyle>
        <color>ff00ff00</color>
        <width>2</width>
      </LineStyle>
    </Style>
    <Style id="gradeBStyle">
      <PolyStyle>
        <color>7fff9000</color>
        <outline>1</outline>
      </PolyStyle>
      <LineStyle>
        <color>ffff9000</color>
        <width>2</width>
      </LineStyle>
    </Style>
    <Style id="gradeCStyle">
      <PolyStyle>
        <color>7f00ffff</color>
        <outline>1</outline>
      </PolyStyle>
      <LineStyle>
        <color>ff00ffff</color>
        <width>2</width>
      </LineStyle>
    </Style>
    <Style id="gradeDStyle">
      <PolyStyle>
        <color>7f0000ff</color>
        <outline>1</outline>
      </PolyStyle>
      <LineStyle>
        <color>ff0000ff</color>
        <width>2</width>
      </LineStyle>
    </Style>
    <Folder>
      <name>All HOLC Grades</name>
'''

for pm in all_placemarks:
    kml += pm + '\n'

kml += '''    </Folder>
  </Document>
</kml>'''

with open('la_all_grades.kml', 'w', encoding='utf-8') as f:
    f.write(kml)

print("Created: la_all_grades.kml")
