"""
Unit and integration tests for Shadowprint FastAPI Web Dashboard endpoints.
"""

import os
import pytest
from fastapi.testclient import TestClient
from shadowprint.web.app import app

client = TestClient(app)


def test_root_serves_spa_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "Shadowprint" in response.text or "doctype html" in response.text.lower()


def test_api_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "docker" in data
    assert "ollama" in data
    assert "database" in data
    assert len(data["engines"]) >= 4


def test_api_fixtures_endpoint():
    response = client.get("/api/fixtures")
    assert response.status_code == 200
    fixtures = response.json()
    assert isinstance(fixtures, list)
    assert len(fixtures) >= 5
    fixture_names = [f["name"] for f in fixtures]
    assert "clean_notes" in fixture_names
    assert "poisoned_weather" in fixture_names
    assert "exfil_calculator" in fixture_names


def test_api_audit_clean_fetch():
    response = client.post("/api/audit", json={"target": "fixtures/clean_fetch"})
    assert response.status_code == 200
    data = response.json()
    assert data["target"] == "clean_fetch"
    assert data["status"] == "PASSED"
    assert data["summary"]["critical"] == 0
    assert len(data["findings"]) == 0


def test_api_audit_poisoned_weather():
    response = client.post("/api/audit", json={"target": "fixtures/poisoned_weather"})
    assert response.status_code == 200
    data = response.json()
    assert data["target"] == "poisoned_weather"
    assert data["status"] in ("FAILED", "FLAGGED")
    # Must catch prompt injection / unicode tag
    categories = [f["category"] for f in data["findings"]]
    assert any("TAG" in c or "INJECTION" in c or "PROMPT" in c for c in categories)


def test_api_pins_and_approve():
    # Approve clean_notes
    resp_approve = client.post("/api/approve", json={"target": "fixtures/clean_notes"})
    assert resp_approve.status_code == 200
    appr_data = resp_approve.json()
    assert appr_data["status"] == "APPROVED"
    assert "definition_hash" in appr_data

    # List pins
    resp_pins = client.get("/api/pins")
    assert resp_pins.status_code == 200
    pins = resp_pins.json()
    assert any(p["server_name"] == "clean_notes" for p in pins)


def test_api_trigger_rugpull_toggle():
    # Enable trigger
    resp_on = client.post("/api/trigger-rugpull", json={"active": True})
    assert resp_on.status_code == 200
    assert resp_on.json()["active"] is True

    # Disable trigger
    resp_off = client.post("/api/trigger-rugpull", json={"active": False})
    assert resp_off.status_code == 200
    assert resp_off.json()["active"] is False
