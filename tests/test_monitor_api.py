import pytest
from app.main import app
from fastapi.testclient import TestClient
from app.db.session import engine, get_db
from sqlalchemy.orm import Session
from app.models.monitor import Monitor
from sqlalchemy import func, select
from datetime import datetime



# Create a local isolated database session
@pytest.fixture
def db_session():
    connection = engine.connect() # connect to the engine created in session.py 
    trans = connection.begin() # begin the one-unit transaction
    session = Session(
        bind = connection, join_transaction_mode="create_savepoint"
    )

    try: 
        yield session
    finally: 
        session.close()
        trans.rollback()
        connection.close()

# Create a test client to run request actions (get, post)
@pytest.fixture
def client(db_session):
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        del app.dependency_overrides[get_db]

# return Monitor count
def count_monitors(db_session):
    return db_session.scalar(select(func.count()).select_from(Monitor))


# Before adding transactional features
def test_create_monitor_returns_saved_monitor(client, db_session):
    response = client.post(
        "/monitors",
        json= {"url": "https://example.com/health"},
        )
    assert response.status_code == 201
    body = response.json()
    assert isinstance(body['id'], int) # checks for if the id is an int
    assert body['url'] == "https://example.com/health"
    assert body['name'] is None
    assert body['is_enabled'] is True
    assert body['check_interval_seconds'] == 60
    assert body['timeout_seconds'] == 5
    assert body['expected_status_code'] == 200
    assert body['created_at'] is not None
    assert body['updated_at'] is not None

    assert db_session.get(Monitor ,body['id']) is not None


def test_create_monitor_preserves_custom_configuration(client, db_session):
    custom_valid_json = {
            "url": "https://example.com/payments/health",
            "name" : "Payments API",
            "check_interval_seconds": 120,
            "timeout_seconds" : 10,
            "expected_status_code" : 204,
            "is_enabled" : False
            }
    
    response = client.post(
        "/monitors",
        json= custom_valid_json 
        )

    
    assert response.status_code == 201
    body = response.json()
    assert isinstance(body['id'], int) # checks for if the id is an int
    assert body['url'] == custom_valid_json['url']
    assert body['name'] == custom_valid_json['name']
    assert body['is_enabled'] is custom_valid_json['is_enabled']
    assert body['check_interval_seconds'] == 120
    assert body['timeout_seconds'] == 10
    assert body['expected_status_code'] == 204
    assert body['created_at'] is not None
    assert body['updated_at'] is not None

    saved_monitor = db_session.get(Monitor ,body['id'])
    assert saved_monitor is not None
    assert saved_monitor.url == custom_valid_json['url']
    assert saved_monitor.name == custom_valid_json['name']
    assert saved_monitor.is_enabled is custom_valid_json['is_enabled']
    assert saved_monitor.check_interval_seconds == 120
    assert saved_monitor.timeout_seconds == 10
    assert saved_monitor.expected_status_code == 204

# ------------------------------------------------------------------------------------
## Testing fail safes all code below expect 422 
# ------------------------------------------------------------------------------------

def test_create_monitor_rejects_interval_below_minimum(client, db_session):
    count_before = count_monitors(db_session)
    response = client.post(
        "/monitors",
        json = {
            "url": "https://example.com/health",
            "name": "custom_test_case",
            "is_enabled": False,
            "check_interval_seconds": 4,
            },
    )
    count_after = count_monitors(db_session)
    assert response.status_code == 422
    assert count_before == count_after

def test_create_monitor_rejects_missing_url(client, db_session):
    count_before = count_monitors(db_session)
    response = client.post(
        "/monitors",
        json = {},
    )
    count_after = count_monitors(db_session)
    assert response.status_code == 422
    assert count_before == count_after

def test_create_monitor_rejects_invalid_url(client, db_session):
    count_before = count_monitors(db_session)
    response = client.post(
        "/monitors",
        json = {
            "url" : "not-a-real-urlDOTcom"
        }
    )
    count_after = count_monitors(db_session)
    assert response.status_code == 422
    assert count_before == count_after

def test_create_monitor_rejects_timeout_equal_to_interval(client, db_session):
    count_before = count_monitors(db_session)
    response = client.post(
        "/monitors",
        json = {
            "url" : "https://example.com/health",
            "check_interval_seconds" : 60,
            "timeout_seconds" : 60,
        }
    )
    count_after = count_monitors(db_session)
    assert count_before == count_after
    assert response.status_code == 422


def test_create_monitor_rejects_default_timeout_equal_to_interval(client, db_session):
    count_before = count_monitors(db_session)
    response = client.post(
        "/monitors",
        json = {
            "url" : "https://example.com/health",
            "check_interval_seconds" : 5,
        }
    )
    count_after = count_monitors(db_session)
    assert response.status_code == 422
    assert count_before == count_after


# ------------------------------------------------------------------------------------
## Testing get requests for read_monitor
# ------------------------------------------------------------------------------------
# # this is a simple test using default config to test if it returns 200
# def test_get_monitor_returns_saved_monitor(client, db_session):
#     monitor = Monitor(url = "https://example.com/health")
#     db_session.add(monitor)
#     db_session.flush()

#     response = client.get(f"/monitors/{monitor.id}")
#     assert response.status_code == 200
#     body = response.json()
#     assert body["id"] == monitor.id
#     assert body["url"] == monitor.url

def test_get_monitor_returns_404_when_missing(client, db_session):
    #arrange - db does not have value from index (n)
    monitor = Monitor(url = "https://example.com/health")
    db_session.add(monitor)
    db_session.flush()
    missing_id = monitor.id
    db_session.delete(monitor)
    db_session.flush()
    response = client.get(f"/monitors/{missing_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Monitor not found"}

def test_get_monitor_returns_200_when_existing(client, db_session):
    monitor = Monitor(
        url= "https://example.com/payments/health",
        name= "Payments API",
        check_interval_seconds= 120,
        timeout_seconds= 10,
        expected_status_code= 204,
        is_enabled= False
    )
    db_session.add(monitor)
    db_session.flush()
    existing_id = monitor.id

    response = client.get(f"/monitors/{existing_id}")
    assert response.status_code == 200
    body = response.json()
    assert body['id'] == existing_id
    assert body['url'] == monitor.url
    assert body['name'] == monitor.name
    assert body['is_enabled'] is monitor.is_enabled
    assert body['check_interval_seconds'] == monitor.check_interval_seconds
    assert body['timeout_seconds'] == monitor.timeout_seconds
    assert body['expected_status_code'] == monitor.expected_status_code
    assert datetime.fromisoformat(body['created_at']) == monitor.created_at
    assert datetime.fromisoformat(body['updated_at']) == monitor.updated_at