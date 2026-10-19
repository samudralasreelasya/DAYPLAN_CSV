"""Tests that highlights are wired into /api/plan-trip and can never break it.

We build a tiny Flask app with only the trip blueprint (so no database is
touched) and replace every external service with a harmless fake.
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
    monkeypatch.setattr(trip_module.overpass_service, "get_hotels", lambda *a, **k: [])
    monkeypatch.setattr(trip_module.restaurant_service, "get_restaurants_with_fallback",
                        lambda *a, **k: [])
    monkeypatch.setattr(trip_module.weather_service, "get_weather", lambda *a, **k: None)
    monkeypatch.setattr(trip_module.budget_service, "estimate_budget", lambda *a, **k: {})
    monkeypatch.setattr(trip_module.ai_service, "generate_itinerary",
                        lambda *a, **k: {"itinerary": [], "packingSuggestions": []})

    app = Flask(__name__)
    app.register_blueprint(trip_bp)
    return app.test_client()


PAYLOAD = {"origin": "Hyderabad", "destination": "Munnar"}


def test_highlights_are_included_and_capped_at_12(client, monkeypatch):
    fake = [{"name": f"Spot{i}", "distanceKm": float(i)} for i in range(20)]
    monkeypatch.setattr(trip_module.highlight_service, "get_highlight_details",
                        lambda *a, **k: {"place": "Munnar", "highlights": fake})
    resp = client.post("/api/plan-trip", json=PAYLOAD)
    assert resp.status_code == 200
    assert len(resp.get_json()["highlights"]) == 12


def test_highlight_failure_does_not_break_the_trip_plan(client, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("highlight service exploded")
    monkeypatch.setattr(trip_module.highlight_service, "get_highlight_details", boom)
    resp = client.post("/api/plan-trip", json=PAYLOAD)
    assert resp.status_code == 200          # the rest of the plan still comes back
    assert resp.get_json()["highlights"] == []