"""Tests for the hotel geocoding script's logic. Nominatim is never called:
the search function is replaced by a fake."""
import importlib.util
import os

import pytest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "geocode_hotels.py")
spec = importlib.util.spec_from_file_location("geocode_hotels", SCRIPT)
gh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gh)

PUNE = (18.5204, 73.8567)
DELHI = (28.6139, 77.2090)


def row(name="Hotel X", city="pune", area="Camp", lat="", lon="", precision=""):
    return {"HotelID": "H001", "Name": name, "City": city, "Area": area, "Category": "budget",
            "Notes": "", "SourceURL": "https://example.com", "Latitude": lat,
            "Longitude": lon, "GeoPrecision": precision}


def test_queries_use_area_then_name_and_city_but_never_area_alone():
    assert gh.build_queries(row("Hotel X", "pune", "Camp")) == [
        "Hotel X, Camp, Pune, India", "Hotel X, Pune, India"]


def test_a_row_without_an_area_gets_one_query():
    assert gh.build_queries(row(area="")) == ["Hotel X, Pune, India"]


def test_a_result_inside_the_city_is_accepted_and_one_in_another_city_rejected():
    assert gh.is_in_city("pune", *PUNE)
    assert not gh.is_in_city("pune", *DELHI)


def test_an_unknown_city_is_never_accepted():
    assert not gh.is_in_city("atlantis", 0.0, 0.0)


def test_blank_rows_are_filled_and_marked_name_match():
    rows = [row()]
    placed, unplaced = gh.geocode_rows(rows, search=lambda q: PUNE, pause=0)
    assert len(placed) == 1 and not unplaced
    assert rows[0]["Latitude"] == "18.520400" and rows[0]["GeoPrecision"] == "name_match"


def test_rows_that_already_have_coordinates_are_not_searched_again():
    calls = []
    rows = [row(lat="18.5", lon="73.8", precision="dataset")]
    gh.geocode_rows(rows, search=lambda q: calls.append(q) or PUNE, pause=0)
    assert calls == [] and rows[0]["GeoPrecision"] == "dataset"


def test_a_wrong_city_result_is_discarded_and_the_next_query_is_tried():
    answers = iter([DELHI, PUNE])                      # first query lands in Delhi, second in Pune
    rows = [row()]
    placed, _ = gh.geocode_rows(rows, search=lambda q: next(answers), pause=0)
    assert len(placed) == 1 and rows[0]["Latitude"] == "18.520400"


def test_a_hotel_that_cannot_be_placed_stays_blank():
    rows = [row()]
    placed, unplaced = gh.geocode_rows(rows, search=lambda q: None, pause=0)
    assert not placed and len(unplaced) == 1
    assert rows[0]["Latitude"] == "" and rows[0]["GeoPrecision"] == ""


def test_only_wrong_city_results_leave_the_row_blank():
    rows = [row()]
    _, unplaced = gh.geocode_rows(rows, search=lambda q: DELHI, pause=0)
    assert len(unplaced) == 1 and rows[0]["Latitude"] == ""


def test_a_row_with_an_unknown_city_is_skipped_without_searching():
    calls = []
    rows = [row(city="atlantis")]
    _, unplaced = gh.geocode_rows(rows, search=lambda q: calls.append(q) or PUNE, pause=0)
    assert calls == [] and len(unplaced) == 1
