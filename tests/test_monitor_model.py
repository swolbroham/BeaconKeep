from app.models.monitor import Monitor
from app.db.session import SessionLocal
from sqlalchemy.exc import IntegrityError, DataError
import pytest

# this creates a temp session for the testing to be used (kinda like when qa uses fake data, except this is a fake db session)
@pytest.fixture
def db_session():
    """create session fixture to test"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_monitor_defaults(db_session):
    monitor = Monitor(url = "https://example.com/health")
    db_session.add(monitor)
    db_session.flush()
    assert monitor.id is not None
    assert monitor.check_interval_seconds == 60
    assert monitor.timeout_seconds == 5
    assert monitor.is_enabled is True
    assert monitor.expected_status_code == 200

def test_monitor_rejects_interval_below_minimum(db_session):
    monitor = Monitor(url = "https://example.com/health")
    monitor.check_interval_seconds = 4
    monitor.timeout_seconds = 1
    db_session.add(monitor)

    with pytest.raises(IntegrityError):
        db_session.flush()

def test_monitor_rejects_interval_above_maximum(db_session):
    monitor = Monitor(url = "https://example.com/health")
    monitor.check_interval_seconds = 3601
    db_session.add(monitor)
    
    with pytest.raises(IntegrityError):
        db_session.flush()

def test_monitor_accepts_minimum_interval(db_session):
    monitor = Monitor(url = "https://example.com/health")
    monitor.check_interval_seconds = 5
    monitor.timeout_seconds = 1
    db_session.add(monitor)
    db_session.flush()

    assert monitor.id is not None

def test_monitor_accepts_maximum_interval(db_session):
    monitor = Monitor(url = "https://example.com/health")
    monitor.check_interval_seconds = 3600
    db_session.add(monitor)
    db_session.flush()

    assert monitor.id is not None


def test_monitor_rejects_timeout_below_minimum(db_session):
    monitor = Monitor(url = "https://example.com/health")
    monitor.timeout_seconds = 0
    db_session.add(monitor)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_monitor_rejects_timeout_equal_to_interval(db_session):
    monitor = Monitor(url = "https://example.com/health")
    monitor.check_interval_seconds = 60
    monitor.timeout_seconds = 60
    db_session.add(monitor)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_monitor_accepts_timeout_below_interval(db_session):
    monitor = Monitor(url = "https://example.com/health")
    monitor.check_interval_seconds = 60
    monitor.timeout_seconds = 59
    db_session.add(monitor)
    db_session.flush()

    assert monitor.id is not None


def test_monitor_rejects_status_code_below_minimum(db_session):
    monitor = Monitor(url = "https://example.com/health")
    monitor.expected_status_code = 199
    db_session.add(monitor)

    with pytest.raises(IntegrityError):
        db_session.flush()

def test_monitor_rejects_status_code_above_maximum(db_session):
    monitor = Monitor(url = "https://example.com/health")
    monitor.expected_status_code = 600
    db_session.add(monitor)

    with pytest.raises(IntegrityError):
        db_session.flush()

def test_monitor_accepts_maximum_status_code(db_session):
    monitor = Monitor(url = "https://example.com/health")
    monitor.expected_status_code = 599
    db_session.add(monitor)
    db_session.flush()

    assert monitor.id is not None

def test_monitor_rejects_missing_url(db_session):
    monitor = Monitor()
    db_session.add(monitor)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_monitor_rejects_timeout_above_interval(db_session):
    monitor = Monitor(url = "https://example.com/health")
    monitor.check_interval_seconds = 60
    monitor.timeout_seconds = 61
    db_session.add(monitor)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_monitor_accepts_missing_name(db_session):
    monitor = Monitor(url = "https://example.com/health")
    db_session.add(monitor)
    db_session.flush()

    assert monitor.name is None


def test_monitor_accepts_maximum_name_length(db_session):
    max_name = "test"*16
    monitor = Monitor(url = "https://example.com/health", name = max_name)
    db_session.add(monitor)
    db_session.flush()

    assert monitor.id is not None

def test_monitor_rejects_name_above_maximum_length(db_session):
    max_name = "test"*16+"i"
    monitor = Monitor(url = "https://example.com/health", name = max_name)
    db_session.add(monitor)

    with pytest.raises(DataError):
        db_session.flush()

def test_monitor_accepts_disabled_state(db_session):
    monitor = Monitor(url = "https://example.com/health", is_enabled = False)
    db_session.add(monitor)
    db_session.flush()

    assert monitor.id is not None
    assert monitor.is_enabled is False

def test_monitor_populates_timestamps(db_session):
    monitor = Monitor(url = "https://example.com/health")
    db_session.add(monitor)
    db_session.flush()

    assert monitor.created_at is not None
    assert monitor.updated_at is not None
    assert monitor.created_at.utcoffset() is not None
    assert monitor.updated_at.utcoffset() is not None

def test_monitor_accepts_duplicate_urls(db_session):
    monitor1 = Monitor(url = "https://example.com/health")
    monitor2 = Monitor(url = "https://example.com/health")
    db_session.add(monitor1)
    db_session.add(monitor2)
    db_session.flush()

    assert monitor1.id is not None
    assert monitor2.id is not None
    assert monitor1.id != monitor2.id


def test_monitor_accepts_duplicate_names(db_session):
    monitor1 = Monitor(url = "https://example.com/health", name = "test")
    monitor2 = Monitor(url = "https://example.com/health", name = "test")
    db_session.add(monitor1)
    db_session.add(monitor2)
    db_session.flush()

    assert monitor1.id is not None
    assert monitor2.id is not None
    assert monitor1.id != monitor2.id
    assert monitor1.name == monitor2.name