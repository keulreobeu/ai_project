from pathlib import Path
import sys

from fastapi.testclient import TestClient


sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app import main


client = TestClient(main.app)


def configure_frontend_dist(monkeypatch, tmp_path):
    dist = tmp_path / "dist"
    assets = dist / "assets"
    assets.mkdir(parents=True)
    (dist / "index.html").write_text("<div id='app'>LocalHub</div>", encoding="utf-8")
    (assets / "app.js").write_text("console.log('LocalHub')", encoding="utf-8")
    monkeypatch.setattr(main, "FRONTEND_DIST", dist)
    return dist


def test_root_serves_built_frontend(monkeypatch, tmp_path):
    configure_frontend_dist(monkeypatch, tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert "LocalHub" in response.text


def test_client_route_falls_back_to_index(monkeypatch, tmp_path):
    configure_frontend_dist(monkeypatch, tmp_path)

    response = client.get("/festivals/1")

    assert response.status_code == 200
    assert "LocalHub" in response.text


def test_built_asset_is_served(monkeypatch, tmp_path):
    configure_frontend_dist(monkeypatch, tmp_path)

    response = client.get("/assets/app.js")

    assert response.status_code == 200
    assert response.text == "console.log('LocalHub')"
    assert "javascript" in response.headers["content-type"]


def test_unknown_api_route_remains_a_json_404(monkeypatch, tmp_path):
    configure_frontend_dist(monkeypatch, tmp_path)

    response = client.get("/api/not-a-real-endpoint")

    assert response.status_code == 404
    assert response.json() == {"detail": "API endpoint not found"}


def test_missing_frontend_build_returns_clear_error(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "FRONTEND_DIST", tmp_path / "missing-dist")

    response = client.get("/")

    assert response.status_code == 503
    assert response.json() == {"detail": "frontend build is not available"}
