from scripts.merge_hotels import merge
from scripts.geocode_hotels import FIELDNAMES


def _existing():
    row = {c: "" for c in FIELDNAMES}
    row.update({"HotelID": "H005", "Name": "The Oberoi, Bengaluru", "City": "bangalore",
                "Category": "luxury", "SourceURL": "https://a.example", "Latitude": "12.9", "Longitude": "77.6"})
    return [row]


def _new(**kw):
    base = {"Name": "Hotel X", "City": "bangalore", "Area": "MG Road", "Category": "budget",
            "Notes": "n", "SourceURL": "https://b.example"}
    base.update(kw)
    return base


def test_adds_new_row_with_next_id_and_keeps_existing_untouched():
    merged, added, skipped = merge(_existing(), [_new()])
    assert added == 1 and skipped == []
    assert merged[0]["Latitude"] == "12.9"              # existing coordinates kept
    assert merged[1]["HotelID"] == "H006" and merged[1]["Latitude"] == ""


def test_duplicate_ignores_case_and_punctuation():
    merged, added, skipped = merge(_existing(), [_new(Name="THE OBEROI BENGALURU")])
    assert added == 0 and skipped[0][1] == "already in Hotels.csv"


def test_same_name_in_other_city_is_not_a_duplicate():
    _, added, _ = merge(_existing(), [_new(Name="The Oberoi Bengaluru", City="delhi")])
    assert added == 1


def test_bad_rows_are_skipped_with_reason_not_fixed():
    rows = [_new(City="atlantis"), _new(Category="fancy"), _new(SourceURL=""), _new(Name="")]
    merged, added, skipped = merge(_existing(), rows)
    assert added == 0 and len(merged) == 1 and len(skipped) == 4


def test_duplicates_inside_the_incoming_file_are_added_once():
    _, added, skipped = merge(_existing(), [_new(), _new()])
    assert added == 1 and skipped[0][1] == "already in Hotels.csv"
