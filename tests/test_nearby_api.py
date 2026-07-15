from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.main import app

client = TestClient(app)


def test_nearby_endpoint_returns_places():
    festivals_response = client.get('/api/festivals?limit=1')
    assert festivals_response.status_code == 200
    payload = festivals_response.json()
    festivals = payload if isinstance(payload, list) else payload['items']
    assert festivals

    festival_id = festivals[0]['id']
    response = client.get(f'/api/festivals/{festival_id}/nearby?radius_km=1&limit=20')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert 'title' in data[0]
        assert all(place['distance_km'] <= 1 for place in data)
        assert [place['distance_km'] for place in data] == sorted(place['distance_km'] for place in data)
        assert len(data) <= 20

    all_response = client.get(f'/api/festivals/{festival_id}/nearby?radius_km=5&all_places=true')
    assert all_response.status_code == 200
    assert all(place['distance_km'] <= 5 for place in all_response.json())


def test_nearby_endpoint_validates_radius():
    response = client.get('/api/festivals/1/nearby?radius_km=0')
    assert response.status_code == 422

    response = client.get('/api/festivals/1/nearby?limit=60')
    assert response.status_code == 422
