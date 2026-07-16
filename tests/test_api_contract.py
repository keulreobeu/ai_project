from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_festivals_endpoint_returns_list():
    response = client.get("/api/festivals")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_festival_detail_endpoint_returns_detail():
    festivals = client.get("/api/festivals").json()
    response = client.get(f"/api/festivals/{festivals[0]['id']}")
    assert response.status_code == 200
    assert "title" in response.json()
    assert response.json()["description"]
    assert response.json()["event_start_date"]
    assert response.json()["event_end_date"]
    assert response.json()["program_summary"]
    assert response.json()["nearby_recommendation"]


def test_festivals_endpoint_supports_pagination():
    response = client.get("/api/festivals", params={"page": 1, "limit": 20})
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert isinstance(payload["items"], list)
    assert payload["page"] == 1
    assert payload["limit"] == 20


def test_festival_detail_endpoint_returns_404_for_missing_festival():
    response = client.get("/api/festivals/999999")
    assert response.status_code == 404
