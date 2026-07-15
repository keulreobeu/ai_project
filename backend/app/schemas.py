from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_count: int
    total_pages: int


class FestivalListResponse(BaseModel):
    items: list["FestivalOut"]
    page: int
    limit: int
    total_count: int
    total_pages: int


class FestivalOut(BaseModel):
    id: int
    title: str
    address: str | None = None
    thumbnail_url: str | None = None
    image_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class FestivalDetailOut(FestivalOut):
    pass


class CalendarFestivalOut(FestivalOut):
    event_start_date: str
    event_end_date: str


class NearbyPlaceOut(BaseModel):
    id: int
    title: str
    address: str | None = None
    category: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    thumbnail_url: str | None = None
    distance_km: float | None = None


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


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2_000)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    lat: float | None = None
    lon: float | None = None
    festival_id: int | None = None
    category: str | None = None
    history: list[ChatMessage] = Field(default_factory=list, max_length=10)


class ChatSourceOut(BaseModel):
    type: Literal["place", "post"] = "place"
    id: int
    title: str
    address: str | None = None
    tel: str | None = None
    category: int | None = None
    distance_km: float | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSourceOut]
