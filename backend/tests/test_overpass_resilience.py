"""Tests for the fail-fast behaviour of overpass_service._query_overpass.

requests.post is replaced by a fake, so no real network call is made.
"""
import logging

import pytest
import requests
from flask import Flask

from services import overpass_service
from utils.errors import UpstreamServiceError


@pytest.fixture(autouse=True)
def app_context(monkeypatch):
    """_query_overpass reads current_app.config, so give it an app, and make
    sure every test starts with the 'Overpass is down' flag cleared."""
    monkeypatch.setattr(overpass_service, "_down_until", 0.0)
    app = Flask(__name__)
    app.config.update(OVERPASS_URL="https://example.invalid/api", USER_AGENT="test-agent")
    with app.app_context():
        yield


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {"elements": []}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}", response=self)

    def json(self):
        return self._payload


def install_fake_post(monkeypatch, behaviour):
    """behaviour() is called per request; it returns a FakeResponse or raises."""
    calls = []

    def fake_post(url, data=None, headers=None, timeout=None):
        calls.append(timeout)
        return behaviour()

    monkeypatch.setattr(overpass_service.requests, "post", fake_post)
    return calls


def raise_timeout():
    raise requests.exceptions.ReadTimeout("read timed out")


def test_success_returns_data_and_does_not_start_cooldown(monkeypatch):
    install_fake_post(monkeypatch, lambda: FakeResponse(200, {"elements": [1, 2]}))
    assert overpass_service._query_overpass("q") == {"elements": [1, 2]}
    assert overpass_service._down_until == 0.0


def test_timeout_starts_cooldown_and_next_call_skips_the_network(monkeypatch):
    calls = install_fake_post(monkeypatch, raise_timeout)
    with pytest.raises(UpstreamServiceError):
        overpass_service._query_overpass("q")
    assert len(calls) == 1

    # Second call during the cooldown must fail instantly WITHOUT calling requests.post.
    with pytest.raises(UpstreamServiceError):
        overpass_service._query_overpass("q")
    assert len(calls) == 1


@pytest.mark.parametrize("status", [429, 500, 502, 504])
def test_server_side_errors_start_cooldown(monkeypatch, status):
    install_fake_post(monkeypatch, lambda: FakeResponse(status))
    with pytest.raises(UpstreamServiceError):
        overpass_service._query_overpass("q")
    assert overpass_service._down_until > 0.0


def test_bad_query_400_does_not_start_cooldown(monkeypatch):
    # A 400 means OUR query is wrong, not that Overpass is struggling.
    calls = install_fake_post(monkeypatch, lambda: FakeResponse(400))
    with pytest.raises(UpstreamServiceError):
        overpass_service._query_overpass("q")
    assert overpass_service._down_until == 0.0
    with pytest.raises(UpstreamServiceError):
        overpass_service._query_overpass("q")
    assert len(calls) == 2          # it really tried again


def test_it_retries_once_the_cooldown_is_over(monkeypatch):
    monkeypatch.setattr(overpass_service, "COOLDOWN_SECONDS", 0)
    calls = install_fake_post(monkeypatch, raise_timeout)
    with pytest.raises(UpstreamServiceError):
        overpass_service._query_overpass("q")
    with pytest.raises(UpstreamServiceError):
        overpass_service._query_overpass("q")
    assert len(calls) == 2          # cooldown of 0 seconds -> no skipping


def test_the_real_reason_is_logged(monkeypatch, caplog):
    install_fake_post(monkeypatch, lambda: FakeResponse(502))
    with caplog.at_level(logging.WARNING):
        with pytest.raises(UpstreamServiceError):
            overpass_service._query_overpass("q")
    assert "HTTP 502" in caplog.text


def test_requests_use_a_short_timeout(monkeypatch):
    calls = install_fake_post(monkeypatch, lambda: FakeResponse(200))
    overpass_service._query_overpass("q")
    connect, read = calls[0]
    assert connect <= 5 and read <= 15