"""Check the along-the-route Overpass query on its own, with long timeouts.

Run from the backend folder:
    python scripts/check_route_query.py route.json

route.json = the "route" object from /api/plan-trip. For each Overpass server
this (1) sends a tiny query, then (2) if that worked, sends the first ~200 km
piece of your route, exactly as the app would, and reports time and results.
It shows whether the SERVER is the problem or the QUERY is.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from config import Config
from services import overpass_service

TINY = '[out:json][timeout:15];node["tourism"="hotel"](around:3000,19.076,72.8777);out count;'
ENDPOINTS = [
    ("app default", Config.OVERPASS_URL),
    ("kumi mirror", "https://overpass.kumi.systems/api/interpreter"),
    ("private.coffee mirror", "https://overpass.private.coffee/api/interpreter"),
]


def post(url, query, timeout):
    start = time.time()
    try:
        r = requests.post(url, data={"data": query},
                          headers={"User-Agent": Config.USER_AGENT}, timeout=timeout)
        return r, round(time.time() - start, 1), None
    except requests.RequestException as e:
        return None, round(time.time() - start, 1), f"{type(e).__name__}: {str(e)[:120]}"


def main(path):
    with open(path, encoding="utf-8-sig") as f:
        coords = json.load(f)["geometry"]["coordinates"]
    waypoints = overpass_service._route_waypoints(coords, overpass_service.ROUTE_STEP_KM)
    piece = waypoints[:overpass_service.ROUTE_POINTS_PER_QUERY]
    query = overpass_service._route_query(piece, 5000)
    print(f"Route has {len(waypoints)} waypoints; first piece = {len(piece)} points\n")

    for label, url in ENDPOINTS:
        r, took, err = post(url, TINY, 30)
        if err or not r.ok:
            print(f"{label:24} tiny query FAILED ({took}s) {err or 'HTTP ' + str(r.status_code)}")
            continue
        print(f"{label:24} tiny query OK ({took}s)")
        r, took, err = post(url, query, 90)
        if err:
            print(f"{'':24} route piece FAILED after {took}s: {err}")
        elif not r.ok:
            print(f"{'':24} route piece HTTP {r.status_code} after {took}s: {r.text[:200]!r}")
        else:
            data = r.json()
            elements = data.get("elements", [])
            names = [e.get("tags", {}).get("name") for e in elements][:8]
            print(f"{'':24} route piece HTTP 200 in {took}s: {len(elements)} places, e.g. {names}")
            if data.get("remark"):
                print(f"{'':24} !! Overpass remark: {data['remark']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts/check_route_query.py route.json")
    main(sys.argv[1])