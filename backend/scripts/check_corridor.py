"""Diagnostic: why did the corridor search find so few stops on a route?

Usage (from the backend folder):
    python scripts/check_corridor.py route.json

route.json is the "route" object returned by /api/plan-trip.
Prints (1) where the route actually runs, (2) the spots closest to it, and
(3) how many spots would qualify at wider corridor widths.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services import corridor_service, local_data_service  # noqa: E402
from utils.geo import RouteIndex  # noqa: E402


def main(path):
    with open(path, encoding="utf-8-sig") as f:
        route = json.load(f)
    coords = route["geometry"]["coordinates"]
    index = RouteIndex(coords)
    print(f"Route: {len(coords)} points, {index.total_km:.0f} km\n")

    print("Where the route runs (every ~100 km):")
    next_mark = 0.0
    for (lon, lat), km in zip(coords, index.start_km.tolist() + [index.total_km]):
        if km >= next_mark:
            print(f"  km {km:6.0f}   lat {lat:.3f}  lon {lon:.3f}")
            next_mark += 100
    print()

    local_data_service.load_all()
    spots = local_data_service.get_all_tourist_spots()
    print(f"Spots in file with coordinates: {len(spots)}")

    rows = []
    for s in spots:
        off, along = index.locate(s["Latitude"], s["Longitude"])
        rows.append((off, along, s["Name"], ",".join(s["tags"][:3])))
    rows.sort()

    for width in (5, 10, 15, 25, 50):
        n = sum(1 for r in rows if r[0] <= width)
        print(f"  within {width:>2} km of the road: {n}")

    print("\n25 spots closest to the road:")
    print(f"  {'off km':>6} {'along km':>8}  name  [tags]")
    for off, along, name, tags in rows[:25]:
        print(f"  {off:6.1f} {along:8.0f}  {name}  [{tags}]")

    print(f"\nWhat get_route_highlights returns now: {len(corridor_service.get_route_highlights(route))} stops")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts/check_corridor.py route.json")
    main(sys.argv[1])