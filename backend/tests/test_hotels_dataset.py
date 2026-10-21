"""Integrity checks on the real data/dataset2/Hotels.csv, so a bad edit (a typo'd
category, a pin in the wrong city, a duplicated hotel) fails loudly."""
import csv
import importlib.util
import os

import pytest

HERE = os.path.dirname(__file__)
CSV_PATH = os.path.join(HERE, "..", "data", "dataset2", "Hotels.csv")
spec = importlib.util.spec_from_file_location(
    "geocode_hotels", os.path.join(HERE, "..", "scripts", "geocode_hotels.py"))
gh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gh)

CATEGORIES = {"luxury", "mid-range", "budget", "unclassified"}
PRECISIONS = {"", "dataset", "name_match"}


@pytest.fixture(scope="module")
def rows():
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == gh.FIELDNAMES
        return list(reader)


def test_the_file_has_hotels(rows):
    assert len(rows) >= 100


def test_ids_are_unique(rows):
    ids = [r["HotelID"] for r in rows]
    assert len(ids) == len(set(ids))


def test_no_hotel_is_listed_twice_in_a_city(rows):
    keys = [(r["City"], r["Name"].lower()) for r in rows]
    assert len(keys) == len(set(keys))


def test_every_city_is_one_we_know_and_every_known_city_has_hotels(rows):
    assert {r["City"] for r in rows} == set(gh.CITY_CENTRES)


def test_categories_are_valid(rows):
    assert {r["Category"] for r in rows} <= CATEGORIES


def test_every_row_names_its_source(rows):
    for r in rows:
        assert r["Name"].strip() and r["SourceURL"].strip(), r["HotelID"]
        assert r["SourceURL"].startswith("https://") or r["SourceURL"].startswith("Tourist_Spots.csv")


def test_coordinates_and_precision_go_together_and_sit_in_the_right_city(rows):
    for r in rows:
        has_lat, has_lon = bool(r["Latitude"].strip()), bool(r["Longitude"].strip())
        assert has_lat == has_lon, r["HotelID"]
        assert r["GeoPrecision"] in PRECISIONS, r["HotelID"]
        assert bool(r["GeoPrecision"]) == has_lat, r["HotelID"]
        if has_lat:
            assert gh.is_in_city(r["City"], float(r["Latitude"]), float(r["Longitude"])), (
                f"{r['Name']} is pinned outside {r['City']}")
