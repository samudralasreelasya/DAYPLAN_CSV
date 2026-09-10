# backend/services/local_data_service.py
"""Loads local CSV datasets once at startup and serves them in-memory.
Keeps the CSVs out of the request/response cycle for speed."""

import os
import logging
import pandas as pd
from utils.geo import haversine_km

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

_citywise_cache = {}             # e.g. {"hyderabad": DataFrame}  (destinations)
_citywise_restaurants_cache = {} # e.g. {"hyderabad": DataFrame}  (restaurants)
_tourist_spots_df = None
_famous_places_df = None


def load_all():
    """Call once from app.py at startup."""
    global _tourist_spots_df, _famous_places_df

    citywise_dir = os.path.join(DATA_DIR, "dataset2", "Citywise Destinations")
    for fname in os.listdir(citywise_dir):
        if fname.startswith("Destinations_") and fname.endswith(".csv"):
            city = fname.replace("Destinations_", "").replace(".csv", "").lower()
            _citywise_cache[city] = pd.read_csv(os.path.join(citywise_dir, fname))

    # Same loading pattern as destinations, applied to the new restaurant
    # fallback dataset. Kept as a separate cache/folder rather than merging
    # into destinations, since restaurants have a different schema
    # (VegStatus, OpeningHours) and are queried independently.
    restaurants_dir = os.path.join(DATA_DIR, "dataset2", "Citywise Restaurants")
    if os.path.isdir(restaurants_dir):
        for fname in os.listdir(restaurants_dir):
            if fname.startswith("Restaurants_") and fname.endswith(".csv"):
                city = fname.replace("Restaurants_", "").replace(".csv", "").lower()
                _citywise_restaurants_cache[city] = pd.read_csv(
                    os.path.join(restaurants_dir, fname)
                )
    else:
        logger.warning(
            "Restaurants folder not found at %s - veg/non-veg fallback will be empty "
            "until CSVs are added.", restaurants_dir
        )

    _tourist_spots_df = pd.read_csv(os.path.join(DATA_DIR, "dataset2", "Tourist_Spots.csv"))
    _famous_places_df = pd.read_csv(os.path.join(DATA_DIR, "dataset1", "world_famous_places_2024.csv"))

    logger.info(
        "Loaded %d cities (destinations), %d cities (restaurants), %d tourist spots, %d famous places",
        len(_citywise_cache), len(_citywise_restaurants_cache),
        len(_tourist_spots_df), len(_famous_places_df)
    )


def get_city_spots(city_name, ref_lat=None, ref_lon=None):
    df = _citywise_cache.get(city_name.lower())
    if df is None:
        return []

    records = df.to_dict(orient="records")

    if ref_lat is not None and ref_lon is not None:
        for r in records:
            r["distanceKm"] = round(
                haversine_km(ref_lat, ref_lon, r["Latitude"], r["Longitude"]), 2
            )
    else:
        for r in records:
            r["distanceKm"] = None

    return records


def get_city_restaurants(city_name, ref_lat=None, ref_lon=None, veg_only=False):
    """Same pattern as get_city_spots, for the curated restaurant fallback.

    veg_only: when True, filters to VegStatus in {"veg", "both"} before
    distance is computed - lets the route layer support a 'show me veg
    options' filter without touching this service's core shape.
    """
    df = _citywise_restaurants_cache.get(city_name.lower())
    if df is None:
        return []

    records = df.to_dict(orient="records")

    if veg_only:
        records = [r for r in records if r.get("VegStatus") in ("veg", "both")]

    for r in records:
        lat, lon = r.get("Latitude"), r.get("Longitude")
        has_coords = pd.notna(lat) and pd.notna(lon)

        # pandas reads a blank CSV cell in a numeric column as float NaN.
        # NaN survives fine inside Python, but jsonify() will emit the
        # literal token `NaN` in the response body - which is NOT valid
        # JSON per spec, and browser JSON.parse() throws on it. Sanitize
        # to None (-> JSON null) here so a row with missing coordinates
        # degrades gracefully instead of corrupting the whole response.
        if not has_coords:
            r["Latitude"] = None
            r["Longitude"] = None

        if has_coords and ref_lat is not None and ref_lon is not None:
            r["distanceKm"] = round(haversine_km(ref_lat, ref_lon, lat, lon), 2)
        else:
            r["distanceKm"] = None

    return records


def get_trending_places(limit=10):
    """Top N famous places by annual visitor count."""
    df = _famous_places_df.sort_values("Annual_Visitors_Millions", ascending=False)
    return df.head(limit).to_dict(orient="records")


def get_famous_places(limit=10):
    return _famous_places_df.head(limit).to_dict(orient="records")
