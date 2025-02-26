import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_debug_invalid_code():
    response = client.post("/debug", json={"code": "print(Hello World)"})
    assert response.status_code == 200
    assert "analysis" in response.json()
