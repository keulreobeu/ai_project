from pydantic import BaseModel, ConfigDict
from datetime import datetime


class FestivalOut(BaseModel):
    id: int
    title: str
    address: str | None = None
    thumbnail_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class FestivalDetailOut(FestivalOut):
    image_url: str | None = None


class NearbyPlaceOut(BaseModel):
    id: int
    title: str
    address: str | None = None
    category: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    thumbnail_url: str | None = None


# Community Post Schemas
class CommunityPostCreate(BaseModel):
    category: str
    title: str
    content: str
    password: str


class CommunityPostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    password: str | None = None


class CommunityPostOut(BaseModel):
    post_id: int
    category: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    view_count: int

    model_config = ConfigDict(from_attributes=True)


class CommunityPostListOut(BaseModel):
    post_id: int
    category: str
    title: str
    created_at: datetime
    view_count: int

    model_config = ConfigDict(from_attributes=True)
