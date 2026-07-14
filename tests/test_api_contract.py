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
    response = client.get("/api/festivals/1")
    assert response.status_code == 200
    assert "title" in response.json()
