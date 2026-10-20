from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db.session import get_db

class FailingSession:
    def execute(self, statement):
        raise OperationalError(
            statement,
            None,
            Exception("Simulated database connection error")
        )
            

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


def test_health_db():
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "database": "connected"
    }

def override_get_db():
    return FailingSession()

# Endpoint failure behavior
def test_failed_db():
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get("/health/db")
        assert response.status_code == 503
        assert response.json() == {
            "status": "unhealthy",
            "database": "disconnected"
        }
    finally:
        del app.dependency_overrides[get_db]
    