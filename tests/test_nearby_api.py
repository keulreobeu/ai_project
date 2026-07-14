from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.main import app

client = TestClient(app)


def test_nearby_endpoint_returns_places():
    response = client.get('/api/festivals/1/nearby')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert 'title' in data[0]
