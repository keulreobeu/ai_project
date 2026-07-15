from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.main import app
from app.models import Region
from app.orm import Base, get_db


TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)
Base.metadata.create_all(bind=TEST_ENGINE)

with TestingSession() as session:
    session.add(Region(region_id=1, region_name="서울"))
    session.commit()


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_post_crud_requires_matching_password_and_never_exposes_it():
    created = client.post(
        "/api/posts",
        json={"region_id": 1, "title": "서울 산책", "content": "한강 산책 후기", "password": "1234"},
    )
    assert created.status_code == 201
    post = created.json()
    assert "password" not in post
    assert "edit_password" not in post

    post_id = post["post_id"]
    denied = client.patch(
        f"/api/posts/{post_id}",
        json={"title": "수정 실패", "password": "0000"},
    )
    assert denied.status_code == 403

    updated = client.patch(
        f"/api/posts/{post_id}",
        json={"title": "서울 야간 산책", "password": "1234"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "서울 야간 산책"

    listed = client.get("/api/posts")
    assert listed.status_code == 200
    assert listed.json()["total_count"] == 1

    wrong_delete = client.request("DELETE", f"/api/posts/{post_id}", json={"password": "0000"})
    assert wrong_delete.status_code == 403

    deleted = client.request("DELETE", f"/api/posts/{post_id}", json={"password": "1234"})
    assert deleted.status_code == 204
    assert client.get(f"/api/posts/{post_id}").status_code == 404
