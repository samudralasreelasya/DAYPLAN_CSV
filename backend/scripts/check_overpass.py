"""Diagnose Overpass connectivity using the SAME URL and User-Agent as the app.

Run from the backend folder:  python scripts\check_overpass.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from config import Config

# Tiny query: how many hotel nodes are within 3 km of central Mumbai?
QUERY = '[out:json][timeout:15];node["tourism"="hotel"](around:3000,19.076,72.8777);out count;'

ENDPOINTS = [
    ("app default", Config.OVERPASS_URL),
    ("kumi mirror", "https://overpass.kumi.systems/api/interpreter"),
    ("private.coffee mirror", "https://overpass.private.coffee/api/interpreter"),
]

print("User-Agent in use:", Config.USER_AGENT)
for label, url in ENDPOINTS:
    start = time.time()
    try:
        r = requests.post(url, data={"data": QUERY},
                          headers={"User-Agent": Config.USER_AGENT}, timeout=20)
        took = round(time.time() - start, 1)
        if r.ok:
            total = r.json()["elements"][0]["tags"]["total"]
            print(f"{label:24} OK    HTTP {r.status_code}  hotel nodes found: {total}  ({took}s)")
        else:
            print(f"{label:24} FAIL  HTTP {r.status_code}  ({took}s)  {r.text[:120]!r}")
    except requests.RequestException as e:
        print(f"{label:24} ERROR {type(e).__name__}: {str(e)[:150]}")