"""Test M72 - Industrial API Endpoints."""
from fastapi.testclient import TestClient

from app.api.server import app

client = TestClient(app)

def test_get_overview():
    response = client.get("/api/v1/industrial/overview")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "feed" in data

def test_get_assets():
    response = client.get("/api/v1/industrial/assets")
    assert response.status_code == 200
    data = response.json()
    assert "assets" in data
    assert len(data["assets"]) > 0

def test_get_asset_details():
    response = client.get("/api/v1/industrial/assets/P-101")
    assert response.status_code == 200
    data = response.json()
    assert "profile" in data
    assert data["profile"]["asset_id"] == "P-101"
    assert "timeline" in data

def test_trigger_rca():
    response = client.post("/api/v1/industrial/assets/P-101/rca", json={"high_vibration": 1.0, "bearing_failure": 1.0, "equipment_failure": 1.0})
    assert response.status_code == 200
    data = response.json()
    assert "root_causes" in data

def test_run_simulation():
    response = client.post("/api/v1/industrial/assets/P-101/simulation?delay_days=30")
    assert response.status_code == 200
    data = response.json()
    assert "baseline_risk" in data

def test_get_decisions():
    response = client.get("/api/v1/industrial/decisions")
    assert response.status_code == 200
    data = response.json()
    assert "interventions" in data
