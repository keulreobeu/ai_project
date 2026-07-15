import hashlib
import hmac
import os
from sqlalchemy.orm import Session
from app.models import Place, CommunityPost
from app.schemas import FestivalOut, FestivalDetailOut, NearbyPlaceOut, CommunityPostCreate, CommunityPostUpdate, CommunityPostOut, CommunityPostListOut
from app.orm import SessionLocal
from datetime import datetime, timedelta, timezone

# 한국시간대 설정
KST = timezone(timedelta(hours=9))

def get_current_kst_time():
    """현재 한국 시간 반환"""
    return datetime.now(KST)


def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"pbkdf2_sha256$100000${salt.hex()}${derived_key.hex()}"


def _verify_password(password: str, stored_password: str | None) -> bool:
    if not stored_password:
        return False

    if stored_password.startswith("pbkdf2_sha256$"):
        try:
            _, iterations_str, salt_hex, derived_hex = stored_password.split("$")
            iterations = int(iterations_str)
            salt = bytes.fromhex(salt_hex)
            derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
            return hmac.compare_digest(derived_key.hex(), derived_hex)
        except ValueError:
            return False

    return stored_password == password


def fetch_festivals(limit: int = 20, keyword: str | None = None):
    db: Session = SessionLocal()
    try:
        query = db.query(Place).filter(Place.content_type_id == 15)
        if keyword:
            query = query.filter(Place.title.like(f"%{keyword}%"))
        rows = query.order_by(Place.place_id).limit(limit).all()
        return [
            FestivalOut(
                id=row.place_id,
                title=row.title or "",
                address=row.address1,
                thumbnail_url=row.thumbnail_url,
                latitude=row.latitude,
                longitude=row.longitude,
            ).model_dump()
            for row in rows
        ]
    finally:
        db.close()


def fetch_festival_detail(festival_id: int):
    db: Session = SessionLocal()
    try:
        row = db.query(Place).filter(Place.place_id == festival_id, Place.content_type_id == 15).first()
        if not row:
            return None
        return FestivalDetailOut(
            id=row.place_id,
            title=row.title or "",
            address=row.address1,
            thumbnail_url=row.thumbnail_url,
            image_url=row.image_url,
            latitude=row.latitude,
            longitude=row.longitude,
        ).model_dump()
    finally:
        db.close()


def fetch_nearby_places(festival_id: int, limit: int = 10):
    db: Session = SessionLocal()
    try:
        festival = db.query(Place).filter(Place.place_id == festival_id, Place.content_type_id == 15).first()
        if not festival or festival.latitude is None or festival.longitude is None:
            return []

        rows = (
            db.query(Place)
            .filter(Place.place_id != festival_id, Place.content_type_id.in_([12, 14, 28, 32, 38]))
            .filter(Place.latitude.isnot(None), Place.longitude.isnot(None))
            .order_by(
                ((Place.latitude - festival.latitude) * (Place.latitude - festival.latitude) +
                 (Place.longitude - festival.longitude) * (Place.longitude - festival.longitude)).asc()
            )
            .limit(limit)
            .all()
        )

        return [
            NearbyPlaceOut(
                id=row.place_id,
                title=row.title or "",
                address=row.address1,
                category=row.content_type_id,
                latitude=row.latitude,
                longitude=row.longitude,
                thumbnail_url=row.thumbnail_url,
            ).model_dump()
            for row in rows
        ]
    finally:
        db.close()


# Community Post Services
def create_community_post(post_data: CommunityPostCreate) -> CommunityPostOut:
    db: Session = SessionLocal()
    try:
        now = get_current_kst_time()
        db_post = CommunityPost(
            category=post_data.category,
            title=post_data.title,
            content=post_data.content,
            password=_hash_password(post_data.password),
            created_at=now,
            updated_at=now,
            view_count=0
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return CommunityPostOut.model_validate(db_post)
    finally:
        db.close()


def get_community_posts(category: str, limit: int = 20) -> list[CommunityPostListOut]:
    db: Session = SessionLocal()
    try:
        posts = db.query(CommunityPost).filter(
            CommunityPost.category == category
        ).order_by(CommunityPost.created_at.desc()).limit(limit).all()
        return [CommunityPostListOut.model_validate(post) for post in posts]
    finally:
        db.close()


def get_community_post(post_id: int) -> CommunityPostOut | None:
    db: Session = SessionLocal()
    try:
        post = db.query(CommunityPost).filter(CommunityPost.post_id == post_id).first()
        if post:
            post.view_count += 1
            db.commit()
            db.refresh(post)
            return CommunityPostOut.model_validate(post)
        return None
    finally:
        db.close()


def update_community_post(post_id: int, post_data: CommunityPostUpdate, password: str) -> CommunityPostOut | None:
    db: Session = SessionLocal()
    try:
        post = db.query(CommunityPost).filter(CommunityPost.post_id == post_id).first()
        if not post or not _verify_password(password, post.password):
            return None

        post.title = post_data.title
        post.content = post_data.content
        if not post.password.startswith("pbkdf2_sha256$"):
            post.password = _hash_password(password)
        post.updated_at = get_current_kst_time()
        db.commit()
        db.refresh(post)
        return CommunityPostOut.model_validate(post)
    finally:
        db.close()


def delete_community_post(post_id: int, password: str) -> bool:
    db: Session = SessionLocal()
    try:
        post = db.query(CommunityPost).filter(CommunityPost.post_id == post_id).first()
        if not post or not _verify_password(password, post.password):
            return False

        db.delete(post)
        db.commit()
        return True
    finally:
        db.close()