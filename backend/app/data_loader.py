import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from pydantic import BaseModel, Field


class PlaceItem(BaseModel):
    contentid: str
    title: str
    addr1: str = ""
    addr2: str = ""
    zipcode: str = ""
    tel: str = ""
    mapx: float
    mapy: float
    firstimage: str = ""
    contentType: str
    contenttypeid: str
    category: str
    distance_km: Optional[float] = None
    raw: Dict[str, object] = Field(default_factory=dict)

    def with_distance(self, lat: float, lon: float) -> "PlaceItem":
        item = self.copy()
        item.distance_km = haversine(lat, lon, self.mapy, self.mapx)
        return item

    def display_address(self) -> str:
        if self.addr2:
            return f"{self.addr1} {self.addr2}".strip()
        return self.addr1


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    from math import asin, cos, radians, sin, sqrt

    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return 6371.0 * c


CATEGORY_FILES = {
    "festival": "서울_축제공연행사.json",
    "tourist": "서울_관광지.json",
    "culture": "서울_문화시설.json",
    "shopping": "서울_쇼핑.json",
    "lodging": "서울_숙박.json",
}

CATEGORY_TITLE = {
    "festival": "축제/공연/행사",
    "tourist": "관광지",
    "culture": "문화시설",
    "shopping": "쇼핑",
    "lodging": "숙박",
}


def load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8-sig") as stream:
        return json.load(stream)


def parse_item(raw: Dict[str, object], category_key: str) -> Optional[PlaceItem]:
    try:
        return PlaceItem(
            contentid=str(raw.get("contentid", "")),
            title=str(raw.get("title", "")).strip(),
            addr1=str(raw.get("addr1", "")).strip(),
            addr2=str(raw.get("addr2", "")).strip(),
            zipcode=str(raw.get("zipcode", "")).strip(),
            tel=str(raw.get("tel", "")).strip(),
            mapx=float(raw.get("mapx", 0) or 0),
            mapy=float(raw.get("mapy", 0) or 0),
            firstimage=str(raw.get("firstimage", "")).strip(),
            contentType=str(raw.get("contentType", CATEGORY_TITLE.get(category_key, ""))).strip(),
            contenttypeid=str(raw.get("contenttypeid", "")).strip(),
            category=category_key,
            raw=raw,
        )
    except (TypeError, ValueError):
        return None


class SeoulDataStore:
    def __init__(self, data_root: Path):
        self.data_root = data_root
        self.categories: Dict[str, List[PlaceItem]] = {}
        self.all_items: List[PlaceItem] = []
        self.load_all()

    def load_category(self, key: str) -> List[PlaceItem]:
        path = self.data_root / CATEGORY_FILES[key]
        content = load_json(path)
        items = content.get("items", [])
        parsed: List[PlaceItem] = []
        for raw_item in items:
            item = parse_item(raw_item, key)
            if item is not None:
                parsed.append(item)
        self.categories[key] = parsed
        return parsed

    def load_all(self) -> None:
        self.all_items = []
        for key in CATEGORY_FILES:
            category_items = self.load_category(key)
            self.all_items.extend(category_items)

    def search_festival(self, query: str, limit: int = 10) -> List[PlaceItem]:
        normalized = query.strip().lower()
        items = self.categories.get("festival", [])
        if not normalized:
            return items[:limit]
        return [
            item
            for item in items
            if normalized in item.title.lower()
            or normalized in item.addr1.lower()
            or normalized in item.addr2.lower()
        ][:limit]

    def find_by_id(self, contentid: str, category: Optional[str] = None) -> Optional[PlaceItem]:
        candidates = self.all_items if category is None else self.categories.get(category, [])
        return next((item for item in candidates if item.contentid == contentid), None)

    def find_festival_by_title(self, title: str) -> Optional[PlaceItem]:
        normalized = title.strip().lower()
        for item in self.categories.get("festival", []):
            if normalized == item.title.lower() or normalized in item.title.lower():
                return item
        return None

    def nearby_items(
        self,
        lat: float,
        lon: float,
        categories: Optional[List[str]] = None,
        radius_km: float = 3.0,
        limit: int = 20,
    ) -> List[PlaceItem]:
        allowed = set(categories) if categories else set(CATEGORY_FILES.keys())
        matches: List[Tuple[float, PlaceItem]] = []
        for item in self.all_items:
            if item.category not in allowed:
                continue
            distance = haversine(lat, lon, item.mapy, item.mapx)
            if distance <= radius_km:
                matches.append((distance, item))
        matches.sort(key=lambda pair: pair[0])
        return [item.with_distance(lat, lon) for distance, item in matches[:limit]]

    def nearby_itinerary(self, event_id: str, radius_km: float = 3.0) -> Dict[str, List[PlaceItem]]:
        event = self.find_by_id(event_id, category="festival")
        if event is None:
            raise ValueError("Festival event not found: %s" % event_id)
        result: Dict[str, List[PlaceItem]] = {}
        for category in ["lodging", "shopping", "culture", "tourist"]:
            result[category] = self.nearby_items(event.mapy, event.mapx, categories=[category], radius_km=radius_km, limit=3)
        return {"event": event, "suggestions": result}

    def recommend_for_persona(
        self,
        persona: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius_km: float = 5.0,
        limit: int = 10,
    ) -> List[PlaceItem]:
        persona = (persona or "").lower()
        if "아이" in persona or "가족" in persona:
            categories = ["festival", "tourist", "culture"]
        elif "연인" in persona:
            categories = ["festival", "culture", "shopping"]
        elif "혼자" in persona:
            categories = ["culture", "tourist"]
        else:
            categories = ["festival", "tourist", "culture", "shopping"]

        if lat is not None and lon is not None:
            return self.nearby_items(lat, lon, categories=categories, radius_km=radius_km, limit=limit)

        results: List[PlaceItem] = []
        for category in categories:
            results.extend(self.categories.get(category, [])[: max(1, limit // len(categories))])
        return results[:limit]

    def format_items_as_text(self, items: Iterable[PlaceItem]) -> str:
        lines: List[str] = []
        for item in items:
            parts = [item.title, CATEGORY_TITLE.get(item.category, item.category), item.display_address()]
            if item.tel:
                parts.append(item.tel)
            if item.distance_km is not None:
                parts.append(f"{item.distance_km:.1f}km")
            lines.append(" | ".join(parts))
        return "\n".join(lines)
