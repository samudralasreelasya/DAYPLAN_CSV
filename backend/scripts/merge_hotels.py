r"""Merge a hotel CSV from a friend into data/dataset2/Hotels.csv.

USAGE (from the backend folder):
    python scripts\merge_hotels.py C:\path\to\friends_file.csv

The friend's file needs these columns:
    Name, City, Area, Category, Notes, SourceURL
Rows are ADDED to Hotels.csv; existing rows (and their coordinates) are never
changed. A row is skipped, with the reason printed, if it
  - is missing a name, city or an https:// SourceURL,
  - uses a city or category we don't know, or
  - is already in Hotels.csv (same city + same name, ignoring case/punctuation).
Nothing is "fixed" silently: you see every skipped row.
Afterwards run  python scripts\geocode_hotels.py  to place the new hotels.
"""
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.geocode_hotels import CITY_CENTRES, CSV_PATH, FIELDNAMES  # noqa: E402

CATEGORIES = {"luxury", "mid-range", "budget", "unclassified"}
REQUIRED = ["Name", "City", "Area", "Category", "Notes", "SourceURL"]


def _key(city, name):
    return city.strip().lower(), re.sub(r"[^a-z0-9]", "", name.lower())


def merge(existing, incoming):
    """Return (merged_rows, added_count, skipped) - skipped is [(name, reason)]."""
    seen = {_key(r["City"], r["Name"]) for r in existing}
    next_id = max([int(r["HotelID"][1:]) for r in existing if r["HotelID"][1:].isdigit()] or [0])
    merged, skipped, added = list(existing), [], 0
    for row in incoming:
        name = (row.get("Name") or "").strip()
        city = (row.get("City") or "").strip().lower()
        category = (row.get("Category") or "").strip().lower()
        url = (row.get("SourceURL") or "").strip()
        if not name or not city:
            skipped.append((name or "(no name)", "missing name or city"))
        elif city not in CITY_CENTRES:
            skipped.append((name, f"unknown city '{city}'"))
        elif category not in CATEGORIES:
            skipped.append((name, f"unknown category '{category}'"))
        elif not url.startswith("https://"):
            skipped.append((name, "missing https:// SourceURL"))
        elif _key(city, name) in seen:
            skipped.append((name, "already in Hotels.csv"))
        else:
            seen.add(_key(city, name))
            next_id += 1
            new = {c: "" for c in FIELDNAMES}
            new.update({"HotelID": f"H{next_id:03d}", "Name": name, "City": city,
                        "Area": (row.get("Area") or "").strip(), "Category": category,
                        "Notes": (row.get("Notes") or "").strip(), "SourceURL": url})
            merged.append(new)
            added += 1
    return merged, added, skipped


def main(friend_path):
    with open(friend_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"Friend's file is missing columns: {missing}")
        incoming = list(reader)
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        existing = list(csv.DictReader(f))
    merged, added, skipped = merge(existing, incoming)
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(merged)
    print(f"Read {len(incoming)} rows: added {added}, skipped {len(skipped)}.")
    for name, why in skipped:
        print(f"  skipped: {name} - {why}")
    print(f"Hotels.csv now has {len(merged)} rows. Next: python scripts\\geocode_hotels.py")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts\\merge_hotels.py friends_file.csv")
    main(sys.argv[1])
