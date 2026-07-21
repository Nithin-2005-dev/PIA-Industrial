import os
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def override_env_cors(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://pia-industrial.example.com, https://another-origin.vercel.app")
    
    import importlib
    import app.api.server
    importlib.reload(app.api.server)
    yield app.api.server.app

def test_cors_allowed_origins(override_env_cors):
    client = TestClient(override_env_cors)
    
    headers = {
        "Origin": "https://pia-industrial.example.com",
        "Access-Control-Request-Method": "GET"
    }
    
    response = client.options("/api/health/industrial", headers=headers)
    
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://pia-industrial.example.com"
    
def test_cors_disallowed_origins(override_env_cors):
    client = TestClient(override_env_cors)
    
    headers = {
        "Origin": "https://malicious-site.com",
        "Access-Control-Request-Method": "GET"
    }
    
    response = client.options("/api/health/industrial", headers=headers)
    
    # Preflight requests for disallowed origins return 400 Bad Request
    assert response.status_code == 400
