from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.main import app

client = TestClient(app)


def test_search_endpoint_filters_by_keyword():
    response = client.get('/api/festivals', params={'keyword': '문학'})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]['title'].find('문학') >= 0
