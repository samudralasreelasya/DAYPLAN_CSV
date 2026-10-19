"""Tests for the along-the-route (corridor) search.

The route is a straight line north along longitude 78 from latitude 10 to 20
(about 1,100 km). Spots are placed at known offsets so the right answer is clear.
"""
import pandas as pd
import pytest

from services import corridor_service, local_data_service

ROUTE = {"geometry": {"coordinates": [[78.0, 10.0], [78.0, 20.0]]}}
KM_PER_DEG_LON = 111.0  # roughly, near the equator-ish latitudes used here


def spot(name, lat, east_km=0.0):
    """A curated spot `east_km` east of the road at the given latitude."""
    return {"Name": name, "Latitude": lat, "Longitude": 78.0 + east_km / KM_PER_DEG_LON,
            "tags": ["scenic"]}


@pytest.fixture
def with_spots(monkeypatch):
    def install(spots):
        monkeypatch.setattr(local_data_service, "get_all_tourist_spots", lambda: list(spots))
    return install


def names(result):
    return [s["name"] for s in result]


def test_spot_inside_the_corridor_is_kept(with_spots):
    with_spots([spot("Near", 15.0, east_km=2)])
    assert names(corridor_service.get_route_highlights(ROUTE)) == ["Near"]


def test_spot_outside_the_corridor_is_dropped(with_spots):
    with_spots([spot("Far", 15.0, east_km=8)])
    assert corridor_service.get_route_highlights(ROUTE) == []


def test_spots_close_to_start_and_end_are_dropped(with_spots):
    # Within 10 km of either end of the route -> "at the start/end", not "on the way".
    with_spots([spot("AtStart", 10.05), spot("AtEnd", 19.95), spot("Middle", 15.0)])
    assert names(corridor_service.get_route_highlights(ROUTE)) == ["Middle"]


def test_results_are_in_travel_order(with_spots):
    with_spots([spot("C", 18.0), spot("A", 12.0), spot("B", 15.0)])
    result = corridor_service.get_route_highlights(ROUTE)
    assert names(result) == ["A", "B", "C"]
    assert [s["alongKm"] for s in result] == sorted(s["alongKm"] for s in result)


def test_each_result_reports_gap_and_position(with_spots):
    with_spots([spot("X", 15.0, east_km=3)])
    item = corridor_service.get_route_highlights(ROUTE)[0]
    assert item["offRouteKm"] == pytest.approx(3.0, abs=0.3)
    assert item["alongKm"] == pytest.approx(556, abs=5)     # ~half of ~1,112 km
    assert item["tags"] == ["scenic"]


def test_one_spot_per_stretch_so_a_dense_area_cannot_crowd_out_the_route(with_spots):
    # Ten spots piled up around latitude 12 (one big city) and one lone spot far
    # along the route. With limit=2 the route is cut into 2 stretches of ~556 km:
    # the city fills the first, the lone spot must still get the second.
    city = [spot(f"City{i}", 12.0 + i * 0.01, east_km=1 + i * 0.1) for i in range(10)]
    with_spots(city + [spot("LoneFarSpot", 18.0, east_km=4)])
    result = corridor_service.get_route_highlights(ROUTE, limit=2)
    assert names(result) == ["City0", "LoneFarSpot"]      # closest city spot + the far one


def test_within_a_stretch_the_spot_closest_to_the_road_wins(with_spots):
    with_spots([spot("Detour", 14.0, east_km=4), spot("Roadside", 14.2, east_km=0.5)])
    result = corridor_service.get_route_highlights(ROUTE, limit=1)
    assert names(result) == ["Roadside"]


def test_a_stretch_contributes_at_most_two_spots(with_spots):
    # All four spots sit in the same stretch of the route: only the two closest to the road stay.
    with_spots([spot("A", 14.0, 1), spot("B", 14.1, 2), spot("C", 14.2, 3), spot("D", 14.3, 4)])
    result = corridor_service.get_route_highlights(ROUTE, limit=3)
    assert names(result) == ["A", "B"]


def test_every_stretch_gets_its_best_spot_before_any_gets_a_second(with_spots):
    # limit=3 cuts the route into 3 stretches. Stretch 1 has two spots that are
    # CLOSER to the road than the single spots in stretches 2 and 3, but the
    # lone spots must still win their slots over stretch 1's second spot.
    with_spots([spot("P1", 11.0, 0.5), spot("P2", 11.5, 0.6),
                spot("Q", 15.0, 4.0), spot("R", 18.0, 4.5)])
    result = corridor_service.get_route_highlights(ROUTE, limit=3)
    assert names(result) == ["P1", "Q", "R"]


def test_never_returns_more_than_the_limit(with_spots):
    with_spots([spot(f"S{i}", 11.0 + i * 0.3, east_km=1) for i in range(30)])
    assert len(corridor_service.get_route_highlights(ROUTE, limit=15)) <= 15


@pytest.mark.parametrize("tag", ["hotel", "hospitality", "restaurant", "restaurants", "cafe", "cuisine"])
def test_hotels_restaurants_and_cafes_are_left_out(with_spots, tag):
    bad = spot("EatSleep", 15.0, east_km=1)
    bad["tags"] = ["shopping", tag]
    with_spots([bad, spot("Sight", 16.0, east_km=1)])
    assert names(corridor_service.get_route_highlights(ROUTE)) == ["Sight"]


@pytest.mark.parametrize("route", [None, {}, {"geometry": None}, {"geometry": {"coordinates": []}},
                                   {"geometry": {"coordinates": [[78.0, 10.0]]}}])
def test_missing_or_unusable_route_gives_empty_list(route, with_spots):
    with_spots([spot("Anything", 15.0)])
    assert corridor_service.get_route_highlights(route) == []


def test_all_tourist_spots_skips_rows_without_coordinates_and_builds_tags(monkeypatch):
    df = pd.DataFrame([
        {"Name": "Good", "Latitude": 10.0, "Longitude": 77.0, "Characteristics": "scenic, tea"},
        {"Name": "NoCoords", "Latitude": float("nan"), "Longitude": 77.0, "Characteristics": "x"},
    ])
    monkeypatch.setattr(local_data_service, "_tourist_spots_df", df)
    spots = local_data_service.get_all_tourist_spots()
    assert [s["Name"] for s in spots] == ["Good"]
    assert spots[0]["tags"] == ["scenic", "tea"]