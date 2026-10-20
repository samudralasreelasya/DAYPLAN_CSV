"""Tests that hotels, restaurants and cafes never show up as 'highlights'.

Tourist_Spots.csv mixes them in with real sights (e.g. Bangalore has hotels and
restaurants tagged 'hotel' / 'restaurant'). get_nearby_highlights must drop them.
"""
import pandas as pd
import pytest

from services import local_data_service

REF = (12.9716, 77.5946)          # central Bangalore


def row(name, tags, dlat=0.0):
    return {"Name": name, "Latitude": REF[0] + dlat, "Longitude": REF[1], "Characteristics": tags}


@pytest.fixture
def with_df(monkeypatch):
    def install(rows):
        monkeypatch.setattr(local_data_service, "_tourist_spots_df", pd.DataFrame(rows))
    return install


def names(result):
    return [r["Name"] for r in result]


def test_sights_are_kept(with_df):
    with_df([row("Cubbon Park", "park, greenery, nature")])
    assert names(local_data_service.get_nearby_highlights(*REF)) == ["Cubbon Park"]


@pytest.mark.parametrize("tag", sorted(local_data_service.EXCLUDED_TAGS))
def test_each_excluded_tag_removes_the_spot(with_df, tag):
    with_df([row("Eat or Sleep", f"shopping, {tag}"), row("Real Sight", "scenic")])
    assert names(local_data_service.get_nearby_highlights(*REF)) == ["Real Sight"]


def test_distance_and_tags_are_still_added_to_kept_spots(with_df):
    with_df([row("Lalbagh", "garden, scenic", dlat=0.01)])
    spot = local_data_service.get_nearby_highlights(*REF)[0]
    assert spot["tags"] == ["garden", "scenic"] and spot["distanceKm"] > 0


def test_the_real_csv_has_no_hotels_or_restaurants_in_bangalore_highlights():
    local_data_service.load_all()
    df = local_data_service._tourist_spots_df
    # guard: the file really does contain such rows near Bangalore, so this test is meaningful
    raw_bad = [
        r for r in df.to_dict(orient="records")
        if local_data_service.EXCLUDED_TAGS & {t.strip() for t in str(r["Characteristics"]).split(",")}
        and abs(r["Latitude"] - REF[0]) < 0.2 and abs(r["Longitude"] - REF[1]) < 0.2
    ]
    assert raw_bad, "expected hotel/restaurant rows near Bangalore in the CSV"

    result = local_data_service.get_nearby_highlights(*REF, radius_km=15)
    assert result
    assert not any(local_data_service.EXCLUDED_TAGS & set(r["tags"]) for r in result)