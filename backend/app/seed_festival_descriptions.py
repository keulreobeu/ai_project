"""Generate and store static festival descriptions from existing TourAPI fields."""

from __future__ import annotations

import html
import json
import re
from datetime import datetime
from math import asin, cos, radians, sin, sqrt

from sqlalchemy import inspect, text

from app.orm import ENGINE


def clean_text(value: object) -> str:
    if not value:
        return ""
    normalized = html.unescape(str(value))
    normalized = re.sub(r"<[^>]+>", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def format_date(value: object) -> str:
    raw = clean_text(value)
    if not raw:
        return ""
    for pattern in ("%Y-%m-%d", "%Y%m%d"):
        try:
            parsed = datetime.strptime(raw, pattern)
            return f"{parsed.year}년 {parsed.month}월 {parsed.day}일"
        except (ValueError, OSError):
            continue
    return raw


def topic_particle(value: str) -> str:
    if not value:
        return "은"
    last = value[-1]
    if "가" <= last <= "힣":
        return "은" if (ord(last) - ord("가")) % 28 else "는"
    return "은"


def summarize_program(value: object, limit: int = 260) -> str:
    program = clean_text(value)
    program = re.sub(r"^(?:[-•]\s*)?(?:주요\s*)?프로그램\s*[:：]\s*", "", program)
    if not program:
        return ""
    summary = program.strip(" -/,")
    if len(summary) > limit:
        summary = summary[:limit].rsplit(" ", 1)[0].rstrip(" ,/") + "…"
    return summary


CATEGORY_LABELS = {12: "관광지", 14: "문화시설", 28: "레포츠", 32: "숙박", 38: "쇼핑"}


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_r, lon1_r, lat2_r, lon2_r = map(radians, (lat1, lon1, lat2, lon2))
    dlat, dlon = lat2_r - lat1_r, lon2_r - lon1_r
    value = sin(dlat / 2) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(dlon / 2) ** 2
    return 6371 * 2 * asin(sqrt(value))


def build_nearby_recommendation(row: dict[str, object], candidates: list[dict[str, object]]) -> str:
    if row.get("latitude") is None or row.get("longitude") is None:
        return "축제 위치 정보가 없어 주변 추천 장소를 선정하지 않았습니다."
    scored = []
    for candidate in candidates:
        if candidate["place_id"] == row["place_id"]:
            continue
        distance = distance_km(
            float(row["latitude"]), float(row["longitude"]),
            float(candidate["latitude"]), float(candidate["longitude"]),
        )
        if distance <= 3:
            scored.append((distance, candidate))
    scored.sort(key=lambda item: (item[0], item[1]["title"] or ""))

    selected = []
    used_categories = set()
    for distance, candidate in scored:
        category = candidate["content_type_id"]
        if category in used_categories:
            continue
        selected.append((distance, candidate))
        used_categories.add(category)
        if len(selected) == 4:
            break
    if not selected:
        return "3km 이내에 함께 추천할 수 있는 등록 장소가 없습니다."
    places = ", ".join(
        f"{candidate['title']}({CATEGORY_LABELS.get(candidate['content_type_id'], '추천 장소')}, 약 {distance:.1f}km)"
        for distance, candidate in selected
    )
    return f"축제 관람 전후에 {places}도 함께 둘러보는 코스를 추천합니다."


def build_description(row: dict[str, object]) -> str:
    source = json.loads(row.get("source_data") or "{}")
    title = clean_text(row.get("title")) or "이 축제"
    place = clean_text(source.get("eventplace")) or clean_text(row.get("address1"))
    start = format_date(row.get("event_start_date"))
    end = format_date(row.get("event_end_date"))
    sponsor = clean_text(source.get("sponsor1"))
    playtime = clean_text(source.get("playtime"))
    fee = clean_text(source.get("usetimefestival"))
    program = summarize_program(source.get("program") or source.get("subevent"))

    if start and end and start != end:
        schedule = f"{start}부터 {end}까지"
    elif start:
        schedule = f"{start}에"
    else:
        schedule = "공식 일정에 따라"

    opening = f"{title}{topic_particle(title)} {schedule} {place or '서울'}에서 열리는 축제입니다."
    details: list[str] = []
    if sponsor:
        details.append(f"{sponsor}가 주최합니다.")
    if program:
        details.append(f"주요 프로그램으로 {program} 등을 만나볼 수 있습니다.")
    if details:
        opening += " " + " ".join(details)

    visit: list[str] = []
    if playtime:
        visit.append(f"운영시간은 {playtime}")
    if fee:
        visit.append(f"이용요금은 {fee}")
    closing = (", ".join(visit) + "입니다. ") if visit else ""
    closing += "세부 일정과 참여 방법은 방문 전 공식 안내를 확인해 주세요."
    return opening + "\n" + closing


def seed_descriptions() -> int:
    columns = {column["name"] for column in inspect(ENGINE).get_columns("places")}
    with ENGINE.begin() as connection:
        if "description" not in columns:
            connection.execute(text("ALTER TABLE places ADD COLUMN description TEXT"))
        if "program_summary" not in columns:
            connection.execute(text("ALTER TABLE places ADD COLUMN program_summary TEXT"))
        if "nearby_recommendation" not in columns:
            connection.execute(text("ALTER TABLE places ADD COLUMN nearby_recommendation TEXT"))
        candidates = [
            dict(row) for row in connection.execute(
                text(
                    "SELECT place_id, title, content_type_id, latitude, longitude FROM places "
                    "WHERE latitude IS NOT NULL AND longitude IS NOT NULL "
                    "AND content_type_id IN (12, 14, 28, 32, 38)"
                )
            ).mappings()
        ]
        rows = connection.execute(
            text(
                "SELECT place_id, title, address1, source_data, event_start_date, event_end_date, latitude, longitude "
                "FROM places WHERE content_type_id = 15 ORDER BY place_id"
            )
        ).mappings()
        descriptions = []
        for row in rows:
            item = dict(row)
            source = json.loads(item.get("source_data") or "{}")
            descriptions.append({
                "place_id": item["place_id"],
                "description": build_description(item),
                "program_summary": summarize_program(source.get("program") or source.get("subevent"))
                    or "등록된 주요 프로그램 정보가 없습니다.",
                "nearby_recommendation": build_nearby_recommendation(item, candidates),
            })
        connection.execute(
            text(
                "UPDATE places SET description = :description, program_summary = :program_summary, "
                "nearby_recommendation = :nearby_recommendation WHERE place_id = :place_id"
            ),
            descriptions,
        )
    return len(descriptions)


if __name__ == "__main__":
    count = seed_descriptions()
    print(f"Seeded {count} festival descriptions.")
