from fastapi.testclient import TestClient
import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.main import app


client = TestClient(app)


def test_calendar_endpoint_returns_festivals_overlapping_month():
    response = client.get("/api/festivals/calendar", params={"year": 2026, "month": 7})

    assert response.status_code == 200
    festivals = response.json()
    assert festivals
    assert all(item["event_start_date"] <= "2026-07-31" for item in festivals)
    assert all(item["event_end_date"] >= "2026-07-01" for item in festivals)


def test_calendar_endpoint_excludes_festivals_without_dates():
    response = client.get("/api/festivals/calendar", params={"year": 2026, "month": 7})

    assert response.status_code == 200
    assert all(item["event_start_date"] and item["event_end_date"] for item in response.json())


def test_calendar_endpoint_validates_month():
    response = client.get("/api/festivals/calendar", params={"year": 2026, "month": 13})

    assert response.status_code == 422
