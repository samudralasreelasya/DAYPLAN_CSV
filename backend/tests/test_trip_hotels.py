"""Tests that /api/plan-trip tells the frontend WHY the hotel list is empty.

Hotels have no CSV fallback, so "the live lookup failed" and "this place has no
hotels in the data" must not look the same to the user.
"""
import pytest
from flask import Flask

from routes import trip as trip_module
from routes.trip import trip_bp


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(trip_module.geocoding_service, "geocode",
                        lambda name: {"lat": 10.0, "lon": 77.0, "name": name})
    monkeypatch.setattr(trip_module.osrm_service, "get_route", lambda *a, **k: None)
    monkeypatch.setattr(trip_module.destination_service, "get_attractions_with_fallback",
                        lambda *a, **k: [])
    monkeypatch.setattr(trip_module.restaurant_service, "get_restaurants_with_fallback",
                        lambda *a, **k: [])
    monkeypatch.setattr(trip_module.highlight_service, "get_highlight_details",
                        lambda *a, **k: {"place": "x", "highlights": []})
    monkeypatch.setattr(trip_module.weather_service, "get_weather", lambda *a, **k: None)
    monkeypatch.setattr(trip_module.budget_service, "estimate_budget", lambda *a, **k: {})
    monkeypatch.setattr(trip_module.ai_service, "generate_itinerary",
                        lambda *a, **k: {"itinerary": [], "packingSuggestions": []})
    monkeypatch.setattr(trip_module.hotel_service, "_load_csv", lambda: ())

    app = Flask(__name__)
    app.register_blueprint(trip_bp)
    return app.test_client()


PAYLOAD = {"origin": "Hyderabad", "destination": "Munnar"}


def test_failed_hotel_lookup_is_reported_as_unavailable(client, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("Overpass is down")
    monkeypatch.setattr(trip_module.overpass_service, "get_hotels", boom)
    body = client.post("/api/plan-trip", json=PAYLOAD).get_json()
    assert body["hotels"] == []
    assert body["hotelsStatus"] == "unavailable"


def test_successful_lookup_is_reported_as_ok(client, monkeypatch):
    monkeypatch.setattr(trip_module.overpass_service, "get_hotels",
                        lambda *a, **k: [{"id": 1, "name": "Hotel A", "distanceKm": 0.5}])
    body = client.post("/api/plan-trip", json=PAYLOAD).get_json()
    assert [h["name"] for h in body["hotels"]] == ["Hotel A"]
    assert body["hotelsStatus"] == "ok"


def test_genuinely_empty_result_is_still_ok_not_unavailable(client, monkeypatch):
    monkeypatch.setattr(trip_module.overpass_service, "get_hotels", lambda *a, **k: [])
    body = client.post("/api/plan-trip", json=PAYLOAD).get_json()
    assert body["hotels"] == []
    assert body["hotelsStatus"] == "ok"