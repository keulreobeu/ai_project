from sqlalchemy.orm import Session
from app.models import Place
from app.schemas import FestivalOut, FestivalDetailOut, NearbyPlaceOut, FestivalListResponse
from app.orm import SessionLocal


def fetch_festivals(page: int | None = None, limit: int | None = None, keyword: str | None = None):
    db: Session = SessionLocal()
    try:
        query = db.query(Place).filter(Place.content_type_id == 15)
        if keyword:
            query = query.filter(Place.title.like(f"%{keyword}%"))

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
