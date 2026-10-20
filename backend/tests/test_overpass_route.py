"""Tests for the along-the-route Overpass search (overpass_service.get_route_places).

requests.post is replaced by a fake, so no real network call is made.
"""
import pytest
import requests
from flask import Flask

from services import overpass_service
from utils.errors import UpstreamServiceError


@pytest.fixture(autouse=True)
def app_context(monkeypatch):
    monkeypatch.setattr(overpass_service, "_down_until", 0.0)
    app = Flask(__name__)
    app.config.update(OVERPASS_URL="https://example.invalid/api", USER_AGENT="test-agent")
    with app.app_context():
        yield


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload
        self.status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def straight_route(km, lon=78.0):
    """A north-going route about `km` long with a point roughly every 1 km."""
    n = int(km)
    return [[lon, 10.0 + i * 0.009] for i in range(n + 1)]


def element(id_, name, lat=10.5, lon=78.01, **tags):
    return {"type": "node", "id": id_, "lat": lat, "lon": lon, "tags": {"name": name, **tags}}


def install_post(monkeypatch, responder):
    """responder(call_number, query, timeout) -> payload dict, or raises."""
    calls = []

    def fake_post(url, data=None, headers=None, timeout=None):
        calls.append({"query": data["data"], "timeout": timeout})
        return FakeResponse(responder(len(calls), data["data"], timeout))

    monkeypatch.setattr(overpass_service.requests, "post", fake_post)
    return calls


# --- thinning the route ---------------------------------------------------------

def test_waypoints_are_thinned_but_keep_both_ends():
    route = straight_route(100)                                   # 101 points, ~1 km apart
    pts = overpass_service._route_waypoints(route, step_km=4.0)
    assert len(pts) < 40
    assert pts[0] == route[0] and pts[-1] == route[-1]


# --- the query --------------------------------------------------------------------

def test_query_lists_points_as_lat_then_lon_and_uses_the_radius():
    query = overpass_service._route_query([[78.5, 10.25], [78.6, 10.35]], radius_m=5000)
    assert "around:5000,10.25,78.5,10.35,78.6" in query            # lat first, then lon
    assert '["name"]' in query                                     # only named places


# --- results ------------------------------------------------------------------------

def test_places_are_parsed_and_unnamed_or_pointless_elements_skipped(monkeypatch):
    payload = {"elements": [
        element(1, "Hill Viewpoint", tourism="viewpoint"),
        {"type": "node", "id": 2, "lat": 10.5, "lon": 78.0, "tags": {"tourism": "viewpoint"}},   # no name
        {"type": "way", "id": 3, "center": {"lat": 10.6, "lon": 78.02},
         "tags": {"name": "Old Dam", "waterway": "dam"}},                                      # way -> centre
        {"type": "node", "id": 4, "tags": {"name": "No Position"}},                            # no lat/lon
    ]}
    install_post(monkeypatch, lambda n, q, t: payload)
    places = overpass_service.get_route_places(straight_route(50))
    assert {p["name"] for p in places} == {"Hill Viewpoint", "Old Dam"}
    dam = next(p for p in places if p["name"] == "Old Dam")
    assert dam["lat"] == 10.6 and dam["tags"] == ["dam"]


def test_a_long_route_is_cut_into_several_queries(monkeypatch):
    calls = install_post(monkeypatch, lambda n, q, t: {"elements": []})
    overpass_service.get_route_places(straight_route(600))
    assert 2 <= len(calls) <= overpass_service.ROUTE_MAX_QUERIES


def test_a_place_found_by_two_overlapping_queries_is_returned_once(monkeypatch):
    install_post(monkeypatch, lambda n, q, t: {"elements": [element(7, "Border Fort", historic="fort")]})
    places = overpass_service.get_route_places(straight_route(600))
    assert [p["name"] for p in places] == ["Border Fort"]


def test_route_queries_use_the_longer_timeout(monkeypatch):
    calls = install_post(monkeypatch, lambda n, q, t: {"elements": []})
    overpass_service.get_route_places(straight_route(50))
    assert calls[0]["timeout"] == overpass_service.ROUTE_REQUEST_TIMEOUT


# --- failures -------------------------------------------------------------------------

def raise_timeout():
    raise requests.exceptions.ReadTimeout("read timed out")


def test_first_query_failing_raises_so_the_caller_can_fall_back(monkeypatch):
    install_post(monkeypatch, lambda n, q, t: raise_timeout())
    with pytest.raises(UpstreamServiceError):
        overpass_service.get_route_places(straight_route(300))


def test_a_later_query_failing_keeps_what_was_already_found(monkeypatch):
    def responder(n, q, t):
        if n == 1:
            return {"elements": [element(1, "First Piece Place")]}
        raise_timeout()
    calls = install_post(monkeypatch, responder)
    places = overpass_service.get_route_places(straight_route(600))
    assert [p["name"] for p in places] == ["First Piece Place"]
    assert len(calls) == 2                                          # it stopped, did not keep hammering


def test_a_slow_route_query_does_not_switch_off_overpass_for_everything_else(monkeypatch):
    install_post(monkeypatch, lambda n, q, t: raise_timeout())
    with pytest.raises(UpstreamServiceError):
        overpass_service.get_route_places(straight_route(300))
    assert overpass_service._down_until == 0.0                      # no cooldown started


def test_when_overpass_is_already_in_cooldown_no_request_is_made(monkeypatch):
    monkeypatch.setattr(overpass_service, "_down_until", overpass_service.time.monotonic() + 100)
    calls = install_post(monkeypatch, lambda n, q, t: {"elements": []})
    with pytest.raises(UpstreamServiceError):
        overpass_service.get_route_places(straight_route(300))
    assert calls == []


def test_it_stops_starting_new_queries_when_the_time_budget_is_spent(monkeypatch):
    clock = {"now": 0.0}
    monkeypatch.setattr(overpass_service.time, "monotonic", lambda: clock["now"])

    def responder(n, q, t):
        clock["now"] += 20.0                                       # every query "takes" 20 s
        return {"elements": [element(n, f"Place{n}")]}

    calls = install_post(monkeypatch, responder)
    places = overpass_service.get_route_places(straight_route(900))
    assert len(calls) == 2                                          # 20 s, 40 s -> over the 30 s budget
    assert len(places) == 2


def test_a_route_with_fewer_than_two_points_gives_nothing():
    assert overpass_service.get_route_places([]) == []
    assert overpass_service.get_route_places([[78.0, 10.0]]) == []