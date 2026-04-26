import pytest

from yougile_resolve import resolve, ResolveAmbiguous, ResolveNotFound


ITEMS = [
    {"id": "00000000-0000-0000-0000-000000000001", "title": "To Do"},
    {"id": "00000000-0000-0000-0000-000000000002", "title": "In Progress"},
    {"id": "00000000-0000-0000-0000-000000000003", "title": "Done"},
    {"id": "00000000-0000-0000-0000-000000000004", "title": "Done (2024)"},
]


def test_uuid_match_returns_item():
    item = resolve("00000000-0000-0000-0000-000000000002", ITEMS)
    assert item["title"] == "In Progress"


def test_uuid_match_when_not_in_list_raises_not_found():
    with pytest.raises(ResolveNotFound):
        resolve("00000000-0000-0000-0000-deadbeefcafe", ITEMS)


def test_exact_name_match_case_insensitive():
    assert resolve("done", ITEMS)["title"] == "Done"
    assert resolve("DONE", ITEMS)["title"] == "Done"


def test_exact_match_wins_over_substring():
    # "Done" is exact; "Done (2024)" contains "Done" as substring.
    # Exact match must win, not flag as ambiguous.
    assert resolve("Done", ITEMS)["title"] == "Done"


def test_substring_unique_match():
    assert resolve("progress", ITEMS)["title"] == "In Progress"


def test_substring_multiple_matches_raises_ambiguous():
    items = [
        {"id": "1", "title": "Backend Done"},
        {"id": "2", "title": "Frontend Done"},
    ]
    with pytest.raises(ResolveAmbiguous) as exc:
        resolve("done", items)
    titles = [c["title"] for c in exc.value.candidates]
    assert "Backend Done" in titles and "Frontend Done" in titles


def test_no_match_raises_not_found():
    with pytest.raises(ResolveNotFound):
        resolve("nonexistent", ITEMS)


def test_empty_list_raises_not_found():
    with pytest.raises(ResolveNotFound):
        resolve("anything", [])
