from pydantic import BaseModel


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
