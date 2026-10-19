"""Tests for RouteIndex: distance from a place to a route, and how far along it is.

Test routes are simple straight lines so the right answer is easy to reason about.
"""
import pytest

from utils.geo import RouteIndex, haversine_km

# A route running straight north along longitude 78, from latitude 10 to 11 (about 111 km).
NORTH_ROUTE = [[78.0, 10.0], [78.0, 11.0]]


def test_total_length_matches_haversine():
    index = RouteIndex(NORTH_ROUTE)
    assert index.total_km == pytest.approx(haversine_km(10, 78, 11, 78), abs=0.01)


def test_place_beside_the_road_gets_gap_and_position():
    index = RouteIndex(NORTH_ROUTE)
    off, along = index.locate(10.5, 78.045)          # halfway up, a little to the east
    assert off == pytest.approx(haversine_km(10.5, 78.0, 10.5, 78.045), abs=0.05)
    assert along == pytest.approx(haversine_km(10.0, 78.0, 10.5, 78.0), abs=0.1)


def test_place_on_the_road_has_zero_gap():
    off, _ = RouteIndex(NORTH_ROUTE).locate(10.3, 78.0)
    assert off == pytest.approx(0.0, abs=0.01)


def test_place_beyond_the_end_snaps_to_the_end_point():
    index = RouteIndex(NORTH_ROUTE)
    off, along = index.locate(11.5, 78.0)
    assert off == pytest.approx(haversine_km(11.0, 78.0, 11.5, 78.0), abs=0.1)
    assert along == pytest.approx(index.total_km, abs=0.01)


def test_place_between_two_far_apart_route_points_is_found():
    # The whole point of Option B: this route has only TWO points, ~111 km apart.
    # A place beside the middle of the road is ~55 km from either point, so a
    # "nearest route point" rule (Option A) would wrongly call it far away.
    index = RouteIndex(NORTH_ROUTE)
    off, _ = index.locate(10.5, 78.01)               # about 1.1 km east of the road
    assert off < 1.5


def test_position_adds_up_across_a_bend():
    # North for ~111 km, then east for a while.
    bend = [[78.0, 10.0], [78.0, 11.0], [79.0, 11.0]]
    index = RouteIndex(bend)
    _, along = index.locate(11.0, 78.5)              # on the eastward leg, halfway
    first_leg = haversine_km(10, 78, 11, 78)
    assert along == pytest.approx(first_leg + haversine_km(11, 78, 11, 78.5), abs=0.2)


def test_duplicate_route_points_do_not_crash():
    index = RouteIndex([[78.0, 10.0], [78.0, 10.0], [78.0, 11.0]])
    off, along = index.locate(10.5, 78.0)
    assert off == pytest.approx(0.0, abs=0.01)
    assert along > 0


@pytest.mark.parametrize("bad", [[], [[78.0, 10.0]]])
def test_a_route_needs_at_least_two_points(bad):
    with pytest.raises(ValueError):
        RouteIndex(bad)