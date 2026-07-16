import hashlib
import hmac
import json
import os
from sqlalchemy.orm import Session
from app.models import Place, CommunityPost
from app.schemas import FestivalOut, FestivalDetailOut, NearbyPlaceOut, CommunityPostCreate, CommunityPostUpdate, CommunityPostOut, CommunityPostListOut
import re
from hmac import compare_digest
from calendar import monthrange
from datetime import date
from math import asin, cos, radians, sin, sqrt
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models import Place
from app.schemas import CalendarFestivalOut, FestivalOut, FestivalDetailOut, NearbyPlaceOut, FestivalListResponse
from app.orm import SessionLocal
from datetime import datetime, timedelta, timezone

# 한국시간대 설정
KST = timezone(timedelta(hours=9))

# TourAPI category codes stored inside Place.source_data.
# The labels are searchable, while API responses continue to use the existing schema.
FESTIVAL_CATEGORY_LABELS = {
    "A02": ("인문", "문화", "예술", "역사"),
    "A0207": ("축제",),
    "A02070200": ("일반축제",),
    "A0208": ("공연", "행사"),
    "A02080100": ("전통공연",),
    "A02080200": ("연극",),
    "A02080500": ("박람회",),
    "A02080600": ("전시회",),
    "A02080800": ("무용",),
    "A02081000": ("대중콘서트", "콘서트"),
    "A02081100": ("영화",),
    "A02081300": ("기타행사",),
}


def _festival_category_codes(keyword: str) -> list[str]:
    normalized_keyword = "".join(keyword.lower().split())
    if not normalized_keyword:
        return []

    return [
        code
        for code, labels in FESTIVAL_CATEGORY_LABELS.items()
        if any(normalized_keyword in "".join(label.lower().split()) for label in labels)
    ]

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


def fetch_festivals(page: int | None = None, limit: int | None = None, keyword: str | None = None):
    db: Session = SessionLocal()
    try:
        query = db.query(Place).filter(Place.content_type_id == 15)
        if keyword:
            stripped_keyword = keyword.strip()
            search_term = f"%{stripped_keyword}%"
            category_codes = _festival_category_codes(stripped_keyword)
            search_conditions = [
                Place.title.like(search_term),
                Place.address1.like(search_term),
                Place.address2.like(search_term),
            ]
            search_conditions.extend(
                func.json_extract(Place.source_data, f"$.{field}") == code
                for code in category_codes
                for field in ("cat1", "cat2", "cat3")
            )
            query = query.filter(
                or_(*search_conditions)
            )

        if page is None and limit is None:
            rows = query.order_by(Place.place_id).limit(20).all()
            return [
                FestivalOut(
                    id=row.place_id,
                    title=row.title or "",
                    address=row.address1,
                    thumbnail_url=row.thumbnail_url,
                    image_url=row.image_url,
                    latitude=row.latitude,
                    longitude=row.longitude,
                ).model_dump()
                for row in rows
            ]

        page = max(1, page or 1)
        limit = max(1, min(limit or 20, 50))
        total_count = query.count()
        rows = query.order_by(Place.place_id).offset((page - 1) * limit).limit(limit).all()
        items = [
            FestivalOut(
                id=row.place_id,
                title=row.title or "",
                address=row.address1,
                thumbnail_url=row.thumbnail_url,
                image_url=row.image_url,
                latitude=row.latitude,
                longitude=row.longitude,
            ).model_dump()
            for row in rows
        ]
        return FestivalListResponse(
            items=items,
            page=page,
            limit=limit,
            total_count=total_count,
            total_pages=max(1, (total_count + limit - 1) // limit),
        ).model_dump()
    finally:
        db.close()


def fetch_festival_detail(festival_id: int):
    db: Session = SessionLocal()
    try:
        row = db.query(Place).filter(Place.place_id == festival_id, Place.content_type_id == 15).first()
        if not row:
            return None
        source = json.loads(row.source_data or "{}")
        return FestivalDetailOut(
            id=row.place_id,
            title=row.title or "",
            address=row.address1,
            thumbnail_url=row.thumbnail_url,
            image_url=row.image_url,
            latitude=row.latitude,
            longitude=row.longitude,
            description=row.description,
            event_start_date=row.event_start_date,
            event_end_date=row.event_end_date,
            event_place=source.get("eventplace"),
            playtime=source.get("playtime"),
            fee=source.get("usetimefestival"),
            program_summary=row.program_summary,
            nearby_recommendation=row.nearby_recommendation,
        ).model_dump()
    finally:
        db.close()


def fetch_calendar_festivals(year: int, month: int):
    month_start = date(year, month, 1).isoformat()
    month_end = date(year, month, monthrange(year, month)[1]).isoformat()
    db: Session = SessionLocal()
    try:
        rows = (
            db.query(Place)
            .filter(Place.content_type_id == 15)
            .filter(Place.event_start_date.isnot(None), Place.event_end_date.isnot(None))
            .filter(Place.event_start_date <= month_end)
            .filter(Place.event_end_date >= month_start)
            .order_by(Place.event_start_date, Place.event_end_date, Place.title)
            .all()
        )
        return [
            CalendarFestivalOut(
                id=row.place_id,
                title=row.title or "",
                address=row.address1,
                thumbnail_url=row.thumbnail_url,
                image_url=row.image_url,
                latitude=row.latitude,
                longitude=row.longitude,
                event_start_date=row.event_start_date,
                event_end_date=row.event_end_date,
            ).model_dump()
            for row in rows
        ]
    finally:
        db.close()


def fetch_nearby_places(festival_id: int, radius_km: float = 3.0, limit: int | None = 10):
    db: Session = SessionLocal()
    try:
        festival = db.query(Place).filter(Place.place_id == festival_id, Place.content_type_id == 15).first()
        if not festival or festival.latitude is None or festival.longitude is None:
            return []

        latitude_delta = radius_km / 111.0
        longitude_scale = max(cos(radians(festival.latitude)), 0.01)
        longitude_delta = radius_km / (111.0 * longitude_scale)
        rows = (
            db.query(Place)
            .filter(Place.place_id != festival_id, Place.content_type_id.in_([12, 14, 28, 32, 38]))
            .filter(Place.latitude.isnot(None), Place.longitude.isnot(None))
            .filter(Place.latitude.between(festival.latitude - latitude_delta, festival.latitude + latitude_delta))
            .filter(Place.longitude.between(festival.longitude - longitude_delta, festival.longitude + longitude_delta))
            .all()
        )

        scored = [
            (row, _haversine_km(festival.latitude, festival.longitude, row.latitude, row.longitude))
            for row in rows
        ]
        scored = [(row, distance) for row, distance in scored if distance <= radius_km]
        scored.sort(key=lambda pair: pair[1])

        selected_places = scored if limit is None else scored[:limit]
        return [
            NearbyPlaceOut(
                id=row.place_id,
                title=row.title or "",
                address=row.address1,
                category=row.content_type_id,
                latitude=row.latitude,
                longitude=row.longitude,
                thumbnail_url=row.thumbnail_url,
                distance_km=round(distance, 3),
            ).model_dump()
            for row, distance in selected_places
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
            updated_at=None,
            view_count=0
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return CommunityPostOut.model_validate(db_post)
    finally:
        db.close()
# ---------------------------------------------------------------------------
# 챗봇 RAG 파이프라인: 1단계(축제 검색) / 3단계(축제 앵커 기준 카테고리별 거리순 조회)
# ---------------------------------------------------------------------------

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlon1, rlat2, rlon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = sin(dlat / 2) ** 2 + cos(rlat1) * cos(rlat2) * sin(dlon / 2) ** 2
    return 6371.0 * 2 * asin(sqrt(a))


def _extract_keywords(question: str) -> List[str]:
    tokens = re.split(r"[\s,.!?~]+", question.strip())
    return [token for token in tokens if len(token) >= 2][:5]


# content_type_id: 12=관광지, 14=문화시설, 15=축제, 28=레포츠, 32=숙박, 38=쇼핑
CATEGORY_LABEL_MAP: Dict[str, List[int]] = {
    "관광지": [12],
    "문화시설": [14],
    "레포츠": [28],
    "숙박": [32],
    "쇼핑": [38],
}

# 자유 텍스트에서 동행/분위기를 감지하기 위한 경량 키워드 사전(형태소 분석기 없이 substring 매칭)
COMPANION_HINT_KEYWORDS: Dict[str, List[str]] = {
    "가족": ["가족", "아이랑", "아이와", "아이들", "키즈", "패밀리"],
    "연인": ["연인", "커플", "데이트", "남자친구", "여자친구"],
    "친구": ["친구"],
    "혼자": ["혼자", "나홀로", "솔로"],
}


def detect_companion_hint(question: str) -> Optional[str]:
    for hint, words in COMPANION_HINT_KEYWORDS.items():
        if any(word in question for word in words):
            return hint
    return None


def search_festivals_for_chat(
    question: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    limit: int = 8,
) -> List[Place]:
    """1단계: 자유 텍스트 질문으로 '축제(15)'만 검색한다.

    지역은 title/address1 LIKE 검색으로, 동행 힌트는 제목 재정렬 휴리스틱으로 반영한다.
    """
    db: Session = SessionLocal()
    try:
        candidates: Dict[int, Place] = {}

        keywords = _extract_keywords(question)
        if keywords:
            query = db.query(Place).filter(Place.content_type_id == 15)
            like_conditions = [Place.title.like(f"%{kw}%") for kw in keywords] + [
                Place.address1.like(f"%{kw}%") for kw in keywords
            ]
            rows = query.filter(or_(*like_conditions)).limit(limit).all()
            for row in rows:
                candidates[row.place_id] = row

        # 키워드 매칭이 없으면(또는 부족하면) 최신 축제 순으로 보충 — 챗봇이 항상 뭔가는 추천하도록
        if len(candidates) < limit:
            fallback_rows = (
                db.query(Place)
                .filter(Place.content_type_id == 15)
                .order_by(Place.place_id.desc())
                .limit(limit - len(candidates))
                .all()
            )
            for row in fallback_rows:
                candidates.setdefault(row.place_id, row)

        results: List[Place] = list(candidates.values())

        # 동행 힌트가 감지되면, 제목에 관련 단어가 포함된 후보를 앞으로 재정렬(매칭 없으면 순서 그대로 유지)
        companion_hint = detect_companion_hint(question)
        if companion_hint:
            hint_words = COMPANION_HINT_KEYWORDS[companion_hint]

            def _hint_sort_key(place: Place) -> bool:
                title = place.title or ""
                return not any(word in title for word in hint_words)

            results.sort(key=_hint_sort_key)

        # 사용자 위치가 있으면 가까운 축제를 우선 노출(정렬만 다시 함, 동행 힌트 재정렬보다 우선)
        if lat is not None and lon is not None:

            def _distance_sort_key(place: Place) -> float:
                if place.latitude is None or place.longitude is None:
                    return float("inf")
                return _haversine_km(lat, lon, place.latitude, place.longitude)

            results.sort(key=_distance_sort_key)

        return results[:limit]
    finally:
        db.close()


def get_place(place_id: int) -> Optional[Place]:
    db: Session = SessionLocal()
    try:
        return db.query(Place).filter(Place.place_id == place_id).first()
    finally:
        db.close()


def nearby_by_category_from_anchor(
    anchor: Place,
    category: str,
    limit: int = 5,
    delta: float = 0.1,  # 약 11km 대응 바운딩 박스
) -> List[Tuple[Place, float]]:
    """3단계: 선택된 축제(anchor) 주변에서 지정 카테고리를 거리순으로 반환한다."""
    allowed_types = CATEGORY_LABEL_MAP.get(category)
    if not allowed_types or anchor.latitude is None or anchor.longitude is None:
        return []

    anchor_lat: float = anchor.latitude
    anchor_lon: float = anchor.longitude

    db: Session = SessionLocal()
    try:
        rows = (
            db.query(Place)
            .filter(Place.content_type_id.in_(allowed_types))
            .filter(Place.place_id != anchor.place_id)
            .filter(Place.latitude.between(anchor_lat - delta, anchor_lat + delta))
            .filter(Place.longitude.between(anchor_lon - delta, anchor_lon + delta))
            .limit(200)
            .all()
        )
        scored: List[Tuple[Place, float]] = [
            (row, _haversine_km(anchor_lat, anchor_lon, row.latitude, row.longitude))
            for row in rows
            if row.latitude is not None and row.longitude is not None
        ]
        scored.sort(key=lambda pair: pair[1])
        return scored[:limit]
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


def search_posts_for_chat(question: str, limit: int = 5) -> list[CommunityPost]:
    keywords = _extract_keywords(question)
    if not keywords:
        return []

    db: Session = SessionLocal()
    try:
        conditions = []
        for keyword in keywords:
            pattern = f"%{keyword}%"
            conditions.extend([CommunityPost.title.like(pattern), CommunityPost.content.like(pattern)])
        return (
            db.query(CommunityPost)
            .filter(or_(*conditions))
            .order_by(CommunityPost.created_at.desc())
            .limit(limit)
            .all()
        )
    finally:
        db.close()
