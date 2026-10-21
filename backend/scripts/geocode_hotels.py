"""Add Latitude/Longitude to data/dataset2/Hotels.csv using Nominatim.

Safe to run again and again: rows that already have coordinates are skipped,
and only rows still missing them are tried.

Two safety rules, because a hotel pin in the wrong city is worse than no pin:
  1. We search by hotel name + area + city (then name + city). We never fall
     back to "just the area", which would give false precision.
  2. A result is accepted only if it lies within MAX_KM_FROM_CENTRE of the
     city's centre. Anything else (a same-named hotel elsewhere) is discarded.

Rows that cannot be placed stay blank; the app still lists them, just without
a distance.

USAGE (from the backend folder):
    python scripts\\geocode_hotels.py
It takes about 2 minutes: Nominatim allows one request per second.
"""
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from utils.geo import haversine_km

CONTACT_EMAIL = "mrecwcsej05me@gmail.com"   # <-- CONFIRM this is still your real email
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = f"DayPlanIPD-StudentProject/1.0 ({CONTACT_EMAIL})"
REFERER = "https://github.com/samudralasreelasya/DAYPLAN_CSV"

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dataset2", "Hotels.csv")
FIELDNAMES = ["HotelID", "Name", "City", "Area", "Category", "Notes",
              "SourceURL", "Latitude", "Longitude", "GeoPrecision"]

MAX_KM_FROM_CENTRE = 40      # resorts around Manali/Munnar sit well outside the town
REQUEST_PAUSE_S = 1.1        # Nominatim usage policy: at most 1 request per second
REQUEST_TIMEOUT_S = 15
MAX_RETRIES = 2

# Approximate city centres, used only to reject results in the wrong place.
CITY_CENTRES = {
    "bangalore": (12.9716, 77.5946), "chandigarh": (30.7333, 76.7794),
    "chennai": (13.0827, 80.2707), "coimbatore": (11.0168, 76.9558),
    "delhi": (28.6139, 77.2090), "guwahati": (26.1445, 91.7362),
    "hyderabad": (17.3850, 78.4867), "kolkata": (22.5726, 88.3639),
    "manali": (32.2396, 77.1887), "mumbai": (19.0760, 72.8777),
    "munnar": (10.0889, 77.0595), "palakkad": (10.7867, 76.6548),
    "pune": (18.5204, 73.8567),
}


def build_queries(row):
    """Search texts to try, most specific first. Never area-only."""
    name, area, city = row["Name"].strip(), row["Area"].strip(), row["City"].strip().title()
    queries = []
    if area:
        queries.append(f"{name}, {area}, {city}, India")
    queries.append(f"{name}, {city}, India")
    return queries


def is_in_city(city, lat, lon):
    centre = CITY_CENTRES.get(city)
    if centre is None:
        return False
    return haversine_km(centre[0], centre[1], lat, lon) <= MAX_KM_FROM_CENTRE


def search_nominatim(query):
    """One query with a couple of retries. Returns (lat, lon) or None."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(
                NOMINATIM_URL,
                params={"q": query, "format": "json", "limit": 1},
                headers={"User-Agent": USER_AGENT, "Referer": REFERER},
                timeout=REQUEST_TIMEOUT_S,
            )
            if resp.status_code == 200:
                results = resp.json()
                if results:
                    return float(results[0]["lat"]), float(results[0]["lon"])
                return None
            print(f"    HTTP {resp.status_code} (attempt {attempt})")
        except requests.RequestException as e:
            print(f"    {type(e).__name__} (attempt {attempt})")
        time.sleep(3 * attempt)
    return None


def geocode_rows(rows, search=search_nominatim, pause=REQUEST_PAUSE_S):
    """Fill in coordinates for rows that lack them. Returns (placed, unplaced)."""
    placed, unplaced = [], []
    for row in rows:
        if row["Latitude"].strip() and row["Longitude"].strip():
            continue                                   # already done
        if row["City"] not in CITY_CENTRES:
            unplaced.append(row)
            continue
        found = None
        for query in build_queries(row):
            hit = search(query)
            time.sleep(pause)
            if hit and is_in_city(row["City"], hit[0], hit[1]):
                found = hit
                break
        if found:
            row["Latitude"], row["Longitude"] = f"{found[0]:.6f}", f"{found[1]:.6f}"
            row["GeoPrecision"] = "name_match"
            placed.append(row)
        else:
            unplaced.append(row)
    return placed, unplaced


def main():
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    todo = sum(1 for r in rows if not (r["Latitude"].strip() and r["Longitude"].strip()))
    print(f"{len(rows)} hotels, {todo} still need coordinates (about {int(todo * 1.5)} s)\n")

    try:
        placed, unplaced = geocode_rows(rows)
    finally:
        # Always save what we have, even if interrupted with Ctrl+C.
        tmp = CSV_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        os.replace(tmp, CSV_PATH)

    print(f"\nPlaced {len(placed)} hotels; {len(unplaced)} left without coordinates.")
    for r in unplaced:
        print(f"  not found: {r['Name']} ({r['City']})")
    print("\nRe-running is safe; it only retries the ones still blank.")


if __name__ == "__main__":
    main()
