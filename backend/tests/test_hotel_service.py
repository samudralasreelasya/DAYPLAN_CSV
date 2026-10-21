import pytest
from services import hotel_service

ROWS = (
    {"HotelID": "H1", "Name": "Grand Munnar", "City": "munnar", "Area": "Town",
     "Category": "luxury", "Notes": "5 star resort", "SourceURL": "http://x",
     "Latitude": "10.09", "Longitude": "77.06", "GeoPrecision": "exact"},
    {"HotelID": "H2", "Name": "Tea Inn", "City": "munnar", "Area": "",
     "Category": "budget", "Notes": "Budget stay", "SourceURL": "http://y",
     "Latitude": "", "Longitude": "", "GeoPrecision": ""},
    {"HotelID": "H3", "Name": "Other City Hotel", "City": "pune", "Area": "",
     "Category": "budget", "Notes": "", "SourceURL": "", "Latitude": "",
     "Longitude": "", "GeoPrecision": ""},
)


@pytest.fixture(autouse=True)
def fake_csv(monkeypatch):
    monkeypatch.setattr(hotel_service, "_load_csv", lambda: ROWS)


def _live(n):
    return [{"id": i, "name": f"Live {i}", "stars": None, "distanceKm": 1.0} for i in range(n)]


def test_csv_filtered_by_city_and_missing_coords_are_null():
    hotels = hotel_service.get_csv_hotels("Munnar, Kerala", 10.09, 77.06)
    assert [h["name"] for h in hotels] == ["Grand Munnar", "Tea Inn"]
    assert hotels[0]["stars"] == 5 and hotels[0]["distanceKm"] == 0.0
    assert hotels[1]["lat"] is None and hotels[1]["distanceKm"] is None


def test_enough_live_hotels_means_no_csv(monkeypatch):
    monkeypatch.setattr(hotel_service.overpass_service, "get_hotels", lambda *a: _live(5))
    hotels, status = hotel_service.get_hotels_with_fallback("Munnar", 10.09, 77.06)
    assert len(hotels) == 5 and status == "ok"


def test_thin_live_result_is_topped_up(monkeypatch):
    monkeypatch.setattr(hotel_service.overpass_service, "get_hotels", lambda *a: _live(1))
    hotels, status = hotel_service.get_hotels_with_fallback("Munnar", 10.09, 77.06)
    assert len(hotels) == 3 and status == "ok"


def test_live_failure_uses_csv(monkeypatch):
    def boom(*a):
        raise RuntimeError("down")
    monkeypatch.setattr(hotel_service.overpass_service, "get_hotels", boom)
    hotels, status = hotel_service.get_hotels_with_fallback("Munnar", 10.09, 77.06)
    assert len(hotels) == 2 and status == "fallback"


def test_live_failure_and_no_csv_is_unavailable(monkeypatch):
    def boom(*a):
        raise RuntimeError("down")
    monkeypatch.setattr(hotel_service.overpass_service, "get_hotels", boom)
    hotels, status = hotel_service.get_hotels_with_fallback("Atlantis", 0.0, 0.0)
    assert hotels == [] and status == "unavailable"


def test_duplicate_names_are_not_repeated(monkeypatch):
    monkeypatch.setattr(hotel_service.overpass_service, "get_hotels",
                        lambda *a: [{"id": 1, "name": "grand munnar", "distanceKm": 0.2}])
    hotels, _ = hotel_service.get_hotels_with_fallback("Munnar", 10.09, 77.06)
    assert [h["name"] for h in hotels].count("Grand Munnar") == 0
    assert len(hotels) == 2