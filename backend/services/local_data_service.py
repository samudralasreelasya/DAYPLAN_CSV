# backend/services/local_data_service.py
"""Loads local CSV datasets once at startup and serves them in-memory.
Keeps the CSVs out of the request/response cycle for speed."""

import os
import logging
import pandas as pd
from utils.geo import haversine_km

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

_citywise_cache = {}       # e.g. {"hyderabad": DataFrame}
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

    _tourist_spots_df = pd.read_csv(os.path.join(DATA_DIR, "dataset2", "Tourist_Spots.csv"))
    _famous_places_df = pd.read_csv(os.path.join(DATA_DIR, "dataset1", "world_famous_places_2024.csv"))

    logger.info(
        "Loaded %d cities, %d tourist spots, %d famous places",
        len(_citywise_cache), len(_tourist_spots_df), len(_famous_places_df)
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


def get_trending_places(limit=10):
    """Top N famous places by annual visitor count."""
    df = _famous_places_df.sort_values("Annual_Visitors_Millions", ascending=False)
    return df.head(limit).to_dict(orient="records")


def get_famous_places(limit=10):
    return _famous_places_df.head(limit).to_dict(orient="records")