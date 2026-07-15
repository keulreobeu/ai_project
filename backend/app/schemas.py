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
>>>>>>> origin/main


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
class PostCreate(BaseModel):
    region_id: int = Field(default=1, ge=1)
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=10_000)
    password: str = Field(min_length=4, max_length=100)


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    content: str | None = Field(default=None, min_length=1, max_length=10_000)
    password: str = Field(min_length=4, max_length=100)

    @model_validator(mode="after")
    def require_change(self):
        if self.title is None and self.content is None:
            raise ValueError("title or content is required")
        return self


class PostPasswordRequest(BaseModel):
    password: str = Field(min_length=4, max_length=100)


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    post_id: int
    region_id: int
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


class PostSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    post_id: int
    region_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class PostListResponse(BaseModel):
    items: list[PostSummary]
    page: int
    limit: int
    total_count: int
    total_pages: int


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
