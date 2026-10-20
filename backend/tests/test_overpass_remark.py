"""Tests that an Overpass 'runtime error' remark is treated as a failure.

Overpass answers HTTP 200 with an EMPTY list and a "remark" when it runs out of
time or memory. Without this check that looks like "nothing found here" - for
hotels it would show "No hotels found" instead of "temporarily unavailable".
"""
import pytest
from flask import Flask

from services import overpass_service
from utils.errors import UpstreamServiceError

REMARK = 'runtime error: Query timed out in "query" at line 3 after 26 seconds.'


@pytest.fixture(autouse=True)
def app_context(monkeypatch):
    monkeypatch.setattr(overpass_service, "_down_until", 0.0)
    app = Flask(__name__)
    app.config.update(OVERPASS_URL="https://example.invalid/api", USER_AGENT="test-agent")
    with app.app_context():
        yield


class FakeResponse:
    status_code = 200

    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def reply_with(monkeypatch, payload):
    monkeypatch.setattr(overpass_service.requests, "post",
                        lambda *a, **k: FakeResponse(payload))


def test_runtime_error_remark_is_a_failure_not_an_empty_result(monkeypatch):
    reply_with(monkeypatch, {"elements": [], "remark": REMARK})
    with pytest.raises(UpstreamServiceError):
        overpass_service._query_overpass("q")


def test_runtime_error_remark_starts_the_cooldown_for_normal_queries(monkeypatch):
    reply_with(monkeypatch, {"elements": [], "remark": REMARK})
    with pytest.raises(UpstreamServiceError):
        overpass_service._query_overpass("q")
    assert overpass_service._down_until > 0.0


def test_runtime_error_remark_does_not_start_the_cooldown_for_route_queries(monkeypatch):
    reply_with(monkeypatch, {"elements": [], "remark": REMARK})
    with pytest.raises(UpstreamServiceError):
        overpass_service._query_overpass("q", trip_cooldown=False)
    assert overpass_service._down_until == 0.0


def test_hotels_report_a_failure_instead_of_an_empty_list(monkeypatch):
    # This is what makes the Hotels page say "temporarily unavailable".
    reply_with(monkeypatch, {"elements": [], "remark": REMARK})
    with pytest.raises(UpstreamServiceError):
        overpass_service.get_hotels(12.97, 77.59)


def test_route_search_raises_on_the_remark_so_the_caller_falls_back(monkeypatch):
    reply_with(monkeypatch, {"elements": [], "remark": REMARK})
    with pytest.raises(UpstreamServiceError):
        overpass_service.get_route_places([[78.0, 10.0], [78.0, 10.5]])


def test_an_unrelated_remark_does_not_break_a_good_answer(monkeypatch):
    payload = {"elements": [{"id": 1}], "remark": "some harmless note"}
    reply_with(monkeypatch, payload)
    assert overpass_service._query_overpass("q") == payload