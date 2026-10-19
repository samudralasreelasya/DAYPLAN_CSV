"""Tests that along-the-route highlights are wired into /api/plan-trip.

Same approach as test_trip_highlights.py: a tiny Flask app with only the trip
blueprint, and every external service replaced by a harmless fake.
"""
import pytest
from flask import Flask

from routes import trip as trip_module
from routes.trip import trip_bp

FAKE_ROUTE = {"distanceKm": 100.0, "durationMinutes": 120,
              "geometry": {"coordinates": [[77.0, 10.0], [78.0, 10.0]]}}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(trip_module.geocoding_service, "geocode",
                        lambda name: {"lat": 10.0, "lon": 77.0, "name": name})
    monkeypatch.setattr(trip_module.osrm_service, "get_route", lambda *a, **k: FAKE_ROUTE)
    monkeypatch.setattr(trip_module.destination_service, "get_attractions_with_fallback",
                        lambda *a, **k: [])
    monkeypatch.setattr(trip_module.overpass_service, "get_hotels", lambda *a, **k: [])
    monkeypatch.setattr(trip_module.restaurant_service, "get_restaurants_with_fallback",
                        lambda *a, **k: [])
    monkeypatch.setattr(trip_module.highlight_service, "get_highlight_details",
                        lambda *a, **k: {"place": "x", "highlights": []})
    monkeypatch.setattr(trip_module.weather_service, "get_weather", lambda *a, **k: None)
    monkeypatch.setattr(trip_module.budget_service, "estimate_budget", lambda *a, **k: {})
    monkeypatch.setattr(trip_module.ai_service, "generate_itinerary",
                        lambda *a, **k: {"itinerary": [], "packingSuggestions": []})

    app = Flask(__name__)
    app.register_blueprint(trip_bp)
    return app.test_client()


PAYLOAD = {"origin": "Hyderabad", "destination": "Munnar"}


def test_route_highlights_are_included(client, monkeypatch):
    fake = [{"name": "Roadside Fort", "alongKm": 42.0, "offRouteKm": 1.2}]
    monkeypatch.setattr(trip_module.corridor_service, "get_route_highlights",
                        lambda route, *a, **k: fake)
    resp = client.post("/api/plan-trip", json=PAYLOAD)
    assert resp.status_code == 200
    assert resp.get_json()["routeHighlights"] == fake


def test_the_osrm_route_is_what_gets_searched(client, monkeypatch):
    seen = {}
    def spy(route, *a, **k):
        seen["route"] = route
        return []
    monkeypatch.setattr(trip_module.corridor_service, "get_route_highlights", spy)
    client.post("/api/plan-trip", json=PAYLOAD)
    assert seen["route"] == FAKE_ROUTE


def test_corridor_failure_does_not_break_the_trip_plan(client, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("corridor exploded")
    monkeypatch.setattr(trip_module.corridor_service, "get_route_highlights", boom)
    resp = client.post("/api/plan-trip", json=PAYLOAD)
    assert resp.status_code == 200
    assert resp.get_json()["routeHighlights"] == []


def test_no_route_gives_empty_route_highlights(client, monkeypatch):
    monkeypatch.setattr(trip_module.osrm_service, "get_route", lambda *a, **k: None)
    resp = client.post("/api/plan-trip", json=PAYLOAD)
    assert resp.status_code == 200
    assert resp.get_json()["routeHighlights"] == []