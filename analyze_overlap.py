#!/usr/bin/env python3
"""
Quantify the spatial correlation between HOLC redlining grades and modern gang
territories for each city.

For every city we compute two complementary metrics, because the gang source
data is not uniform (some cities are mapped as polygon territories, some only as
point markers, most are a mix):

  1. AREA overlap  - of the total gang-territory polygon area, what % falls
     inside HOLC Grade A / B / C / D zones (and what % is outside any graded
     zone). Only meaningful where polygons exist.

  2. POINT overlap - of the gang point markers, what % fall inside each grade.
     This is the only metric available for point-only cities (e.g. Chicago).

We also compute a BASELINE: the share of each city's total HOLC-mapped area that
is Grade D. Comparing the gang Grade-D share against this baseline gives a
"disproportionality" ratio (>1 means gangs are over-represented in redlined
areas relative to how much of the mapped city was redlined).

Dependencies: shapely + lxml only (no geopandas/pyproj in this environment), so
KML is parsed by hand and areas are computed in a local equal-area (equirect-
angular about the city centroid) projection - exact enough for within-city
ratios.

Output: analysis.csv  (machine-readable, one row per city)
        plus a printed summary table.
"""

import csv
import json
import math
import os
from collections import defaultdict

from lxml import etree
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree

ROOT = os.path.dirname(os.path.abspath(__file__))
GANG_DIR = os.path.join(ROOT, "gang_territories")

KML_NS = "{http://www.opengis.net/kml/2.2}"

# city key -> (holc geojson, gang kml). LA's gang file lives under chrome-automation/.
CITIES = {
    "los_angeles":   ("los_angeles_holc.geojson",   os.path.join("chrome-automation", "la_gang_territories.kml")),
    "chicago":       ("chicago_holc.geojson",       os.path.join("gang_territories", "chicago_gangs.kml")),
    "detroit":       ("detroit_holc.geojson",       os.path.join("gang_territories", "detroit_gangs.kml")),
    "philadelphia":  ("philadelphia_holc.geojson",  os.path.join("gang_territories", "philadelphia_gangs.kml")),
    "cleveland":     ("cleveland_holc.geojson",     os.path.join("gang_territories", "cleveland_gangs.kml")),
    "st_louis":      ("st_louis_holc.geojson",      os.path.join("gang_territories", "st_louis_gangs.kml")),
    "baltimore":     ("baltimore_holc.geojson",     os.path.join("gang_territories", "baltimore_gangs.kml")),
    "pittsburgh":    ("pittsburgh_holc.geojson",    os.path.join("gang_territories", "pittsburgh_gangs.kml")),
    "san_francisco": ("san_francisco_holc.geojson", os.path.join("gang_territories", "san_francisco_gangs.kml")),
    "new_orleans":   ("new_orleans_holc.geojson",   os.path.join("gang_territories", "new_orleans_gangs.kml")),
    "atlanta":       ("atlanta_holc.geojson",       os.path.join("gang_territories", "atlanta_gangs.kml")),
    "new_york_city": ("new_york_city_holc.geojson", os.path.join("gang_territories", "new_york_city_gangs.kml")),
}

DISPLAY = {
    "los_angeles": "Los Angeles", "chicago": "Chicago", "detroit": "Detroit",
    "philadelphia": "Philadelphia", "cleveland": "Cleveland", "st_louis": "St. Louis",
    "baltimore": "Baltimore", "pittsburgh": "Pittsburgh", "san_francisco": "San Francisco",
    "new_orleans": "New Orleans", "atlanta": "Atlanta", "new_york_city": "New York City",
}

GRADES = ["A", "B", "C", "D"]
EARTH_R = 6371008.8  # mean Earth radius (m)


def make_projector(lat0_deg):
    """Local equirectangular projection (lon/lat degrees -> metres) about lat0.
    Area-faithful enough for within-city ratios over a metro-scale extent."""
    lat0 = math.radians(lat0_deg)
    kx = EARTH_R * math.cos(lat0) * math.pi / 180.0
    ky = EARTH_R * math.pi / 180.0

    def project(lon, lat):
        return (lon * kx, lat * ky)

    return project


# ---------- HOLC (GeoJSON) ----------

def load_holc(path):
    """Return {grade: shapely geometry (lon/lat)} plus the dataset centroid lat."""
    with open(path) as f:
        data = json.load(f)

    by_grade = defaultdict(list)
    lat_sum = lat_n = 0.0
    for feat in data["features"]:
        grade = feat["properties"].get("grade")
        if grade:
            grade = grade.strip()
        if grade not in GRADES:
            continue
        geom = feat["geometry"]
        polys = []
        if geom["type"] == "Polygon":
            polys = [geom["coordinates"]]
        elif geom["type"] == "MultiPolygon":
            polys = geom["coordinates"]
        for rings in polys:
            shell = rings[0]
            holes = rings[1:]
            try:
                p = Polygon(shell, holes)
                if not p.is_valid:
                    p = p.buffer(0)
                if not p.is_empty:
                    by_grade[grade].append(p)
                    for lon, lat in shell:
                        lat_sum += lat
                        lat_n += 1
            except Exception:
                continue

    lat0 = lat_sum / lat_n if lat_n else 0.0
    merged = {g: unary_union(by_grade[g]) for g in GRADES if by_grade[g]}
    return merged, lat0


# ---------- Gangs (KML) ----------

def _parse_coords(text):
    pts = []
    for tok in text.split():
        parts = tok.split(",")
        if len(parts) >= 2:
            pts.append((float(parts[0]), float(parts[1])))
    return pts


def load_gangs(path):
    """Return (list of gang polygons, list of gang points) in lon/lat."""
    tree = etree.parse(path)
    root = tree.getroot()

    polygons, points = [], []
    for poly_el in root.iter(f"{KML_NS}Polygon"):
        outer = poly_el.find(f"{KML_NS}outerBoundaryIs/{KML_NS}LinearRing/{KML_NS}coordinates")
        if outer is None or not outer.text:
            continue
        shell = _parse_coords(outer.text)
        if len(shell) < 3:
            continue
        holes = []
        for inner in poly_el.findall(f"{KML_NS}innerBoundaryIs/{KML_NS}LinearRing/{KML_NS}coordinates"):
            if inner.text:
                ring = _parse_coords(inner.text)
                if len(ring) >= 3:
                    holes.append(ring)
        try:
            p = Polygon(shell, holes)
            if not p.is_valid:
                p = p.buffer(0)
            if not p.is_empty:
                polygons.append(p)
        except Exception:
            continue

    for pt_el in root.iter(f"{KML_NS}Point"):
        c = pt_el.find(f"{KML_NS}coordinates")
        if c is not None and c.text:
            cs = _parse_coords(c.text)
            if cs:
                points.append(Point(cs[0]))

    return polygons, points


# ---------- projection helpers ----------

def project_geom(geom, project):
    from shapely.ops import transform
    return transform(lambda x, y, z=None: project(x, y), geom)


def analyze_city(key):
    holc_file, gang_file = CITIES[key]
    holc_path = os.path.join(ROOT, holc_file)
    gang_path = os.path.join(ROOT, gang_file)
    if not (os.path.exists(holc_path) and os.path.exists(gang_path)):
        print(f"  skip {key}: missing files")
        return None

    holc_ll, lat0 = load_holc(holc_path)
    project = make_projector(lat0)
    holc = {g: project_geom(geom, project) for g, geom in holc_ll.items()}

    gpolys_ll, gpts = load_gangs(gang_path)
    gpolys = [project_geom(p, project) for p in gpolys_ll]

    # --- baseline: share of mapped HOLC area by grade ---
    holc_area = {g: holc[g].area if g in holc else 0.0 for g in GRADES}
    total_holc = sum(holc_area.values())
    baseline = {g: (holc_area[g] / total_holc * 100 if total_holc else 0.0) for g in GRADES}

    row = {"city": DISPLAY[key]}

    # --- AREA overlap ---
    if gpolys:
        gang_union = unary_union(gpolys)
        total_gang_area = gang_union.area
        area_in = {}
        for g in GRADES:
            if g in holc:
                inter = gang_union.intersection(holc[g])
                area_in[g] = inter.area
            else:
                area_in[g] = 0.0
        accounted = sum(area_in.values())
        outside = max(total_gang_area - accounted, 0.0)
        row["n_gang_polygons"] = len(gpolys)
        for g in GRADES:
            row[f"area_pct_{g}"] = round(area_in[g] / total_gang_area * 100, 1) if total_gang_area else ""
        row["area_pct_outside"] = round(outside / total_gang_area * 100, 1) if total_gang_area else ""
        # conditional: distribution among gang area that falls INSIDE a graded zone
        for g in GRADES:
            row[f"area_in_pct_{g}"] = round(area_in[g] / accounted * 100, 1) if accounted else ""
    else:
        row["n_gang_polygons"] = 0
        for g in GRADES:
            row[f"area_pct_{g}"] = ""
            row[f"area_in_pct_{g}"] = ""
        row["area_pct_outside"] = ""

    # --- POINT overlap (STRtree for speed) ---
    if gpts:
        gpts_proj = [project_geom(pt, project) for pt in gpts]
        graded = [(g, holc[g]) for g in GRADES if g in holc]
        geoms = [geom for _, geom in graded]
        tree = STRtree(geoms) if geoms else None
        pt_in = {g: 0 for g in GRADES}
        outside_pts = 0
        for pt in gpts_proj:
            hit_grade = None
            if tree is not None:
                for idx in tree.query(pt):
                    g, geom = graded[idx]
                    if geom.contains(pt):
                        hit_grade = g
                        break
            if hit_grade:
                pt_in[hit_grade] += 1
            else:
                outside_pts += 1
        n = len(gpts_proj)
        inside = n - outside_pts
        row["n_gang_points"] = n
        for g in GRADES:
            row[f"point_pct_{g}"] = round(pt_in[g] / n * 100, 1) if n else ""
            row[f"point_in_pct_{g}"] = round(pt_in[g] / inside * 100, 1) if inside else ""
        row["point_pct_outside"] = round(outside_pts / n * 100, 1) if n else ""
    else:
        row["n_gang_points"] = 0
        for g in GRADES:
            row[f"point_pct_{g}"] = ""
            row[f"point_in_pct_{g}"] = ""
        row["point_pct_outside"] = ""

    for g in GRADES:
        row[f"baseline_pct_{g}"] = round(baseline[g], 1)

    # Disproportionality for Grade D, computed apples-to-apples: gang D-share
    # CONDITIONAL on falling within a graded zone, vs the baseline D-share of
    # graded area. >1 = gangs over-represented in redlined areas. Prefer the
    # area metric; fall back to points (point-only cities like Chicago).
    gang_d = row["area_in_pct_D"] if row["area_in_pct_D"] != "" else row["point_in_pct_D"]
    if gang_d != "" and baseline["D"] > 0:
        row["D_disproportionality"] = round(gang_d / baseline["D"], 2)
    else:
        row["D_disproportionality"] = ""

    return row


def main():
    fieldnames = [
        "city", "n_gang_polygons", "n_gang_points",
        "area_pct_A", "area_pct_B", "area_pct_C", "area_pct_D", "area_pct_outside",
        "area_in_pct_A", "area_in_pct_B", "area_in_pct_C", "area_in_pct_D",
        "point_pct_A", "point_pct_B", "point_pct_C", "point_pct_D", "point_pct_outside",
        "point_in_pct_A", "point_in_pct_B", "point_in_pct_C", "point_in_pct_D",
        "baseline_pct_A", "baseline_pct_B", "baseline_pct_C", "baseline_pct_D",
        "D_disproportionality",
    ]
    rows = []
    for key in CITIES:
        print(f"Analyzing {DISPLAY[key]}...")
        r = analyze_city(key)
        if r:
            rows.append(r)

    out = os.path.join(ROOT, "analysis.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {out}")

    # printed summary: gang grade distribution CONDITIONAL on being within a
    # graded zone, vs the city's baseline D-share. Dx>1 = gangs concentrate in
    # redlined (D) areas more than the city's redlining footprint alone implies.
    print("\n" + "=" * 92)
    print("GANG TERRITORY GRADE DISTRIBUTION (within HOLC-mapped area) vs REDLINING BASELINE")
    print("Dx = gang D-share / baseline D-share.  Dx > 1 means gangs concentrate in redlined zones.")
    print("=" * 92)
    print(f"{'City':<15}{'metric':<7}{'A%':>6}{'B%':>6}{'C%':>6}{'D%':>7}   {'baseD%':>7}{'Dx':>6}")
    print("-" * 92)
    n_dispro = 0
    for r in rows:
        if r["area_in_pct_D"] != "":
            metric = "area"
            a, b, c, d = (r[f"area_in_pct_{g}"] for g in GRADES)
        else:
            metric = "point"
            a, b, c, d = (r[f"point_in_pct_{g}"] for g in GRADES)
        dx = r["D_disproportionality"]
        if dx != "" and dx > 1:
            n_dispro += 1
        print(f"{r['city']:<15}{metric:<7}{a:>6}{b:>6}{c:>6}{d:>7}   {r['baseline_pct_D']:>7}{dx:>6}")
    print("-" * 92)
    print(f"{n_dispro} of {len(rows)} cities show gang territory disproportionately in redlined (D) zones (Dx > 1).")


if __name__ == "__main__":
    main()
