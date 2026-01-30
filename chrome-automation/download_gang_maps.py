#!/usr/bin/env python3
"""Download gang territory KML files from Google My Maps."""

import urllib.request
import os

# Gang territory map IDs for each city
GANG_MAPS = {
    "chicago": "1xe7X8O0tiDRdJUNqG8IHEkcYaqyQOSs",
    "detroit": "1CqZGEDsnlpF0z7TZy8oGtxHo0q9uqNg",
    "philadelphia": "170j6JIjSRYraeh1xGf-auKlR6HnRuBo",
    "cleveland": "1a3vq_epf5x8xi_Ja8OvUqWaWb7PUkas",
    "st_louis": "1BlP8dWqpsrwljeqkQGarSa57mbzJfq0",
    "baltimore": "1mpCVI7qXDuOes-4utDr2FK3HSsMbzRM",
    "pittsburgh": "1as3Dn6-Ecu69l66mU-5ifD0ycZk",
    "san_francisco": "1PD1YdFZWhv_-1o6ZulmPoLMkQAM",
    "new_orleans": "1zeodrS0XnUt8IximIS9-pmx7OR8Dl8A",
    "atlanta": "1hMEvQwd1n9Jccxsy-1LzhwozIXkzpz8",
    "new_york_city": "1CMk3O2D9HcjSdc8W5mepDj30JENpR48f",
}

OUTPUT_DIR = "/mnt/d/AI_Projects/redlining_project/gang_territories"

def download_kml(city, map_id):
    """Download KML from Google My Maps."""
    url = f"https://www.google.com/maps/d/kml?mid={map_id}&forcekml=1"
    output_path = os.path.join(OUTPUT_DIR, f"{city}_gangs.kml")

    print(f"Downloading {city}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            with open(output_path, 'wb') as f:
                f.write(data)

        size_kb = len(data) / 1024
        print(f"  ✓ {city}: {size_kb:.1f} KB")
        return True
    except Exception as e:
        print(f"  ✗ {city}: {e}")
        return False

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 50)
    print("Downloading Gang Territory Maps")
    print("=" * 50)
    print()

    success = 0
    failed = []

    for city, map_id in GANG_MAPS.items():
        if download_kml(city, map_id):
            success += 1
        else:
            failed.append(city)

    print()
    print("=" * 50)
    print(f"Done: {success}/{len(GANG_MAPS)} downloaded")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 50)

if __name__ == "__main__":
    main()
