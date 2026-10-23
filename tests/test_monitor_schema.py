from app.schemas.monitor import MonitorCreate
from pydantic import ValidationError
import pytest


def test_monitor_create_applies_defaults():
    monitor = MonitorCreate(url = "https://example.com/health")
    assert monitor.check_interval_seconds == 60
    assert monitor.timeout_seconds == 5
    assert monitor.is_enabled is True
    assert monitor.expected_status_code == 200

def test_monitor_create_trims_name():
    monitor = MonitorCreate(name = " test ", url = "https://example.com/health")
    assert monitor.name == "test"

def test_monitor_create_converts_blank_name_to_none():
    monitor = MonitorCreate(name = "  ", url = "https://example.com/health")
    assert monitor.name is None

def test_monitor_create_rejects_timeout_equal_to_interval():
    with pytest.raises(ValidationError):
        MonitorCreate(
            url = "https://example.com/health",
            check_interval_seconds = 60,
            timeout_seconds = 60
            )

def test_monitor_create_rejects_default_timeout_equal_to_interval():
    with pytest.raises(ValidationError):
        MonitorCreate(
            url = "https://example.com/health",
            check_interval_seconds = 5
            )


def test_monitor_create_rejects_missing_url():
    with pytest.raises(ValidationError):
        MonitorCreate()


def test_monitor_create_rejects_malformed_url():
    with pytest.raises(ValidationError):
        MonitorCreate(url = "not-a-url")

def test_monitor_create_rejects_unsupported_url_scheme():
    with pytest.raises(ValidationError):
        MonitorCreate(url = "ftp://example.com")

def test_monitor_create_accepts_http_url():
    monitor = MonitorCreate(url="http://example.com")
    assert monitor.url.scheme == "http"


def test_monitor_create_accepts_https_url():
    monitor = MonitorCreate(url="https://example.com")
    assert monitor.url.scheme == "https"