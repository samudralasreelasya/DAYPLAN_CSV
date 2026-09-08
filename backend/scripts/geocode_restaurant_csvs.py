"""
Geocoding script v3 - adds Latitude/Longitude to the curated
Restaurants_<city>.csv files using Nominatim.

CHANGES FROM v2:
1. Per-ROW skip logic instead of per-file. Safe to re-run: only rows
   still missing Latitude get a new attempt, already-geocoded rows are
   left alone. This matters because most rows failing now are genuine
   "not in OpenStreetMap's database" cases (small local restaurants),
   not errors - re-running gains a little each time as transient
   timeouts clear up, without re-spending calls on rows that already
   worked.
2. Restored the two-tier fallback query (specific name+area, then just
   area) - this was in v1, removed in v2 on a wrong guess that request
   VOLUME was causing the 403s. The real cause was the placeholder email
   in the User-Agent (now fixed), so it's safe to bring the fallback
   back - it should noticeably raise the success rate, since areas/
   neighbourhoods (e.g. "Sector 1", "Mylapore") are almost always in
   OSM even when small named businesses aren't.
3. Longer timeout (15s) to reduce spurious timeout retries.

BEFORE RUNNING: CONTACT_EMAIL must already be your real email from the
v2 fix - this script keeps that requirement.

USAGE (safe to run multiple times):
    cd backend
    python scripts\\geocode_restaurant_csvs.py
"""

import csv
import os
import time
import requests

CONTACT_EMAIL = "mrecwcsej05me@gmail.com"  # <-- CONFIRM this is still your real email

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = f"DayPlanIPD-StudentProject/1.0 ({CONTACT_EMAIL})"
REFERER = "https://github.com/samudralasreelasya/DAYPLAN_CSV"

CSV_DIR = os.path.join(
    os.path.dirname(__file__), "..", "data", "dataset2", "Citywise Restaurants"
)

FIELDNAMES = [
    "RestaurantID", "Name", "Category", "Type", "VegStatus",
    "Area", "OpeningHours", "Notes", "SourceURL", "Latitude", "Longitude",
]

MAX_RETRIES = 2
BASE_BACKOFF_SECONDS = 3


def _single_query(query):
    """One query attempt with its own retry loop for transient errors.
    Returns (lat, lon) or (None, None)."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(
                NOMINATIM_URL,
                params={"q": query, "format": "json", "limit": 1},
                headers={"User-Agent": USER_AGENT, "Referer": REFERER},
                timeout=15,
            )
            if resp.status_code == 403:
                wait = BASE_BACKOFF_SECONDS * attempt
                print(f"    403 (attempt {attempt}/{MAX_RETRIES}), waiting {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            results = resp.json()
            if not results:
                return None, None  # genuine "not found" - no point retrying
            return float(results[0]["lat"]), float(results[0]["lon"])
        except (requests.RequestException, KeyError, ValueError, IndexError) as e:
            wait = BASE_BACKOFF_SECONDS * attempt
            print(f"    error (attempt {attempt}/{MAX_RETRIES}): {e}; waiting {wait}s...")
            time.sleep(wait)
    return None, None


def geocode_row(name, area, city_name):
    """Try the specific name+area query first, then fall back to just the
    area if that returns nothing - a real neighbourhood is far more likely
    to be in OSM than a small local business."""
    lat, lon = _single_query(f"{name}, {area}, {city_name}, India")
    if lat is not None:
        return lat, lon, "name+area"

    lat, lon = _single_query(f"{area}, {city_name}, India")
    if lat is not None:
        return lat, lon, "area-only (approximate)"

    return None, None, "not found"


def process_file(path, city_name):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Ensure Latitude/Longitude keys exist on every row even if this file
    # was never geocoded before.
    for r in rows:
        r.setdefault("Latitude", "")
        r.setdefault("Longitude", "")

    todo = [r for r in rows if not r["Latitude"]]
    if not todo:
        print(f"[{city_name}] all {len(rows)} rows already geocoded, skipping.")
        return

    print(f"[{city_name}] {len(todo)} of {len(rows)} rows still need geocoding...")
    for i, row in enumerate(todo, start=1):
        lat, lon, method = geocode_row(row["Name"], row["Area"], city_name)
        row["Latitude"] = lat if lat is not None else ""
        row["Longitude"] = lon if lon is not None else ""
        print(f"  [{i}/{len(todo)}] {row['Name']}: {lat}, {lon} ({method})")
        time.sleep(1.5)

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    still_missing = sum(1 for r in rows if not r["Latitude"])
    print(f"[{city_name}] done. {still_missing}/{len(rows)} rows still blank (genuinely not in OSM - safe to leave, or fill in manually).\n")


def main():
    if CONTACT_EMAIL == "your-real-email@example.com":
        raise SystemExit("Set CONTACT_EMAIL to your real email before running.")

    if not os.path.isdir(CSV_DIR):
        raise SystemExit(f"Folder not found: {CSV_DIR}")

    for fname in sorted(os.listdir(CSV_DIR)):
        if fname.startswith("Restaurants_") and fname.endswith(".csv"):
            city_name = fname.replace("Restaurants_", "").replace(".csv", "")
            process_file(os.path.join(CSV_DIR, fname), city_name)


if __name__ == "__main__":
    main()
