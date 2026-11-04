import pytest
from app.main import app
from fastapi.testclient import TestClient
from app.db.session import engine, get_db
from sqlalchemy.orm import Session
from app.models.monitor import Monitor




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


@pytest.fixture
def client(db_session):
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        del app.dependency_overrides[get_db]


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