"""Tests for the highlights resilience logic.

We never call the real Overpass API or read the real CSV here. Instead we
replace the two data sources with fakes, so every test is fast, repeatable and
can simulate failures on demand.
"""
import pytest

from services import highlight_service

LAT, LON = 10.0889, 77.0595  # roughly Munnar; the value is irrelevant to the fakes


def live_spot(name, distance):
    """Shape returned by overpass_service.get_highlights (no 'tags' key)."""
    return {"id": 1, "name": name, "category": "highlight",
            "lat": 10.0, "lon": 77.0, "distanceKm": distance}


def csv_spot(name, distance):
    """Shape returned by local_data_service.get_nearby_highlights."""
    return {"Name": name, "Latitude": 10.0, "Longitude": 77.0,
            "distanceKm": distance, "tags": ["tea", "scenic"]}


def use_fakes(monkeypatch, live=None, live_error=None, csv=None):
    """Swap the two data sources for fakes."""
    def fake_overpass(lat, lon, radius_m=5000):
        if live_error:
            raise live_error
        return list(live or [])

    monkeypatch.setattr(highlight_service.overpass_service, "get_highlights", fake_overpass)
    monkeypatch.setattr(
        highlight_service.local_data_service, "get_nearby_highlights",
        lambda lat, lon, radius_km=10: list(csv or []),
    )


# ---- failure mode 1: the whole API call fails ----------------------------

def test_overpass_down_falls_back_to_csv(monkeypatch):
    use_fakes(monkeypatch, live_error=Exception("Service temporarily unavailable"),
              csv=[csv_spot("A", 1.0), csv_spot("B", 2.0)])
    result = highlight_service.get_highlights_with_fallback("Munnar", LAT, LON)
    assert [h["name"] for h in result] == ["A", "B"]
    assert all(h["category"] == "highlight (curated)" for h in result)


def test_overpass_down_and_csv_empty_returns_empty_list(monkeypatch):
    use_fakes(monkeypatch, live_error=Exception("down"), csv=[])
    assert highlight_service.get_highlights_with_fallback("Nowhere", LAT, LON) == []


# ---- failure mode 2: the API answers but with too little ------------------

def test_sparse_live_results_are_blended_with_csv(monkeypatch):
    use_fakes(monkeypatch, live=[live_spot("Live1", 1.5), live_spot("Live2", 3.0)],
              csv=[csv_spot("Csv1", 0.5), csv_spot("Csv2", 2.0), csv_spot("Csv3", 4.0)])
    result = highlight_service.get_highlights_with_fallback("Munnar", LAT, LON)
    names = [h["name"] for h in result]
    # blend, not replace: the live spots are still there...
    assert "Live1" in names and "Live2" in names
    # ...and the curated ones were added
    assert {"Csv1", "Csv2", "Csv3"} <= set(names)
    assert len(result) == 5


@pytest.mark.parametrize("live_count, expect_blend", [
    (0, True), (4, True),     # below the threshold -> blend
    (5, False), (8, False),   # at or above the threshold -> live only
])
def test_sparse_threshold_boundary(monkeypatch, live_count, expect_blend):
    live = [live_spot(f"Live{i}", float(i)) for i in range(live_count)]
    use_fakes(monkeypatch, live=live, csv=[csv_spot("Csv1", 0.1)])
    result = highlight_service.get_highlights_with_fallback("Munnar", LAT, LON)
    has_curated = any(h["category"] == "highlight (curated)" for h in result)
    assert has_curated is expect_blend


# ---- ordering and output shape --------------------------------------------

def test_results_are_sorted_nearest_first(monkeypatch):
    use_fakes(monkeypatch, live=[live_spot("Far", 9.0)],
              csv=[csv_spot("Near", 0.2), csv_spot("Mid", 4.0)])
    result = highlight_service.get_highlights_with_fallback("Munnar", LAT, LON)
    distances = [h["distanceKm"] for h in result]
    assert distances == sorted(distances)


def test_details_shape_and_missing_tags_default_to_empty_list(monkeypatch):
    # Live Overpass results carry no 'tags' key; the route-facing shape must
    # still give the frontend a list so tag chips never crash.
    live = [live_spot(f"Live{i}", float(i)) for i in range(5)]
    use_fakes(monkeypatch, live=live)
    details = highlight_service.get_highlight_details("Munnar", LAT, LON)
    assert details["place"] == "Munnar"
    first = details["highlights"][0]
    assert set(first) == {"name", "category", "tags", "distanceKm", "lat", "lon"}
    assert first["tags"] == []