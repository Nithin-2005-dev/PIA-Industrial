import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def override_env_cors(monkeypatch):
    # Set the exact environment variable Render uses
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://pia-industrial-kappa.vercel.app,http://localhost:5173")
    
    import importlib
    import app.api.server
    importlib.reload(app.api.server)
    yield app.api.server.app

def test_cors_workspaces_vercel_origin(override_env_cors):
    client = TestClient(override_env_cors)
    
    headers = {
        "Origin": "https://pia-industrial-kappa.vercel.app",
    }
    
    # Preflight test
    options_response = client.options("/api/v1/industrial/workspaces", headers={**headers, "Access-Control-Request-Method": "GET"})
    assert options_response.status_code == 200
    assert options_response.headers.get("access-control-allow-origin") == "https://pia-industrial-kappa.vercel.app"
    
    # Actual GET request test
    get_response = client.get("/api/v1/industrial/workspaces", headers=headers)
    assert get_response.status_code == 200
    assert get_response.headers.get("access-control-allow-origin") == "https://pia-industrial-kappa.vercel.app"

def test_cors_overview_vercel_origin(override_env_cors):
    client = TestClient(override_env_cors)
    
    headers = {
        "Origin": "https://pia-industrial-kappa.vercel.app",
    }
    
    get_response = client.get("/api/v1/industrial/overview?workspace_id=demo-p101", headers=headers)
    assert get_response.status_code == 200
    assert get_response.headers.get("access-control-allow-origin") == "https://pia-industrial-kappa.vercel.app"

def test_cors_localhost_origin(override_env_cors):
    client = TestClient(override_env_cors)
    
    headers = {
        "Origin": "http://localhost:5173",
    }
    
    get_response = client.get("/api/v1/industrial/workspaces", headers=headers)
    assert get_response.status_code == 200
    assert get_response.headers.get("access-control-allow-origin") == "http://localhost:5173"
