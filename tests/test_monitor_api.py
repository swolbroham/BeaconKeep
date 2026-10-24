import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_monitor_returns_created_status():
    response = client.post("/monitors", json={"url":"https://example.com/health"})
    assert response.status_code == 201