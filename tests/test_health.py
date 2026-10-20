from app.main import app
from fastapi.testclient import TestClient



client = TestClient(app)

# Gets health status code
def test_health_status_code():
    response = client.get("/health")
    assert response.status_code == 200

# Gets health response
def test_health_response():
    response = client.get("/health")
    assert response.json() == {
        "status": "healthy",
        "service": "BeaconKeep"
    }

# Endpoint must return an empty JSON object
def test_health_db():
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "database": "connected"
    }


# Endpoint failure behavior
def test_failed_db():
    response = client.get("/health/db")
    assert response.status_code == 503
    assert response.json() == {
        "status": "unhealthy",
        "database": "disconnected"
    }