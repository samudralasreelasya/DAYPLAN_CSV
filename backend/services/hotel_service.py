"""Hotels: live Overpass first, curated CSV (dataset2/Hotels.csv) as backup.

Status values returned to the frontend:
  ok          live data was used (or the CSV topped up a thin live result)
  fallback    the live lookup failed, so CSV hotels are shown instead
  unavailable the live lookup failed and the CSV has nothing for this place
"""
import csv
import logging
import math
import os
import re
from functools import lru_cache

from services import overpass_service

logger = logging.getLogger(__name__)

_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "dataset2", "Hotels.csv",
)
MIN_LIVE = 5  # below this many live hotels, blend in CSV hotels


def _haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _to_float(value):
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _stars(notes):
    m = re.search(r"(\d)\s*-?\s*star", notes or "", re.I)
    return int(m.group(1)) if m else None


@lru_cache(maxsize=1)
def _load_csv():
    try:
        with open(_CSV_PATH, encoding="utf-8-sig", newline="") as f:
            return tuple(csv.DictReader(f))
    except OSError as e:
        logger.error("Could not read Hotels.csv: %s", e)
        return ()


def get_csv_hotels(destination, lat, lon):
    dest = (destination or "").lower()
    out = []
    for row in _load_csv():
        city = (row.get("City") or "").strip().lower()
        if not city or city not in dest:
            continue
        h_lat = _to_float(row.get("Latitude"))
        h_lng = _to_float(row.get("Longitude"))
        dist = None
        if h_lat is not None and h_lng is not None:
            dist = round(_haversine_km(lat, lon, h_lat, h_lng), 1)
        out.append({
            "id": "csv-" + (row.get("HotelID") or row.get("Name") or ""),
            "name": row.get("Name"),
            "stars": _stars(row.get("Notes")),
            "distanceKm": dist,
            "lat": h_lat,
            "lng": h_lng,
            "area": row.get("Area") or None,
            "category": row.get("Category") or None,
            "notes": row.get("Notes") or None,
            "sourceUrl": row.get("SourceURL") or None,
            "source": "dataset",
        })
    out.sort(key=lambda h: (h["distanceKm"] is None, h["distanceKm"] or 0, h["name"] or ""))
    return out


def get_hotels_with_fallback(destination, lat, lon):
    """Returns (hotels, status)."""
    live, live_failed = [], False
    try:
        live = [dict(h, source=h.get("source", "live"))
                for h in (overpass_service.get_hotels(lat, lon) or [])]
    except Exception as e:
        logger.error("Overpass get_hotels failed: %s", e)
        live_failed = True

    if len(live) >= MIN_LIVE:
        return live, "ok"

    seen = {(h.get("name") or "").strip().lower() for h in live}
    extra = [h for h in get_csv_hotels(destination, lat, lon)
             if (h["name"] or "").strip().lower() not in seen]
    merged = live + extra

    if live_failed:
        return merged, ("fallback" if merged else "unavailable")
    return merged, "ok"