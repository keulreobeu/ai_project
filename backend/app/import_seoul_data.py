import json
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "서울"
DB_PATH = ROOT / "project" / "seoul_festival.db"

SCHEMA_SQL = ROOT / "project" / "seoul_festival_schema.sql"

CONTENT_TYPE_MAP = {
    12: "tourist_attraction",
    14: "culture_facility",
    15: "festival_event",
    28: "leports",
    32: "accommodation",
    38: "shopping",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))
    conn.commit()
    conn.close()


def import_places(conn, region_id: int):
    files = [
        "서울_축제공연행사.json",
        "서울_관광지.json",
        "서울_숙박.json",
        "서울_레포츠.json",
        "서울_문화시설.json",
        "서울_쇼핑.json",
    ]

    for filename in files:
        payload = load_json(DATA_DIR / filename)
        content_type_id = int(payload.get("contentTypeId", 0))
        if content_type_id not in CONTENT_TYPE_MAP:
            continue

        for item in payload.get("items", []):
            conn.execute(
                """
                INSERT INTO places (
                    region_id, content_type_id, external_content_id, title, address1, address2,
                    zipcode, tel, latitude, longitude, thumbnail_url, image_url, map_level,
                    source_data, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    region_id,
                    content_type_id,
                    item.get("contentid"),
                    item.get("title"),
                    item.get("addr1"),
                    item.get("addr2"),
                    item.get("zipcode"),
                    item.get("tel"),
                    float(item.get("mapy") or 0) if item.get("mapy") else None,
                    float(item.get("mapx") or 0) if item.get("mapx") else None,
                    item.get("firstimage2") or item.get("firstimage"),
                    item.get("firstimage"),
                    item.get("mlevel"),
                    filename,
                    item.get("createdtime"),
                    item.get("modifiedtime"),
                ),
            )

    conn.commit()


def build_relationships(conn):
    festival_rows = conn.execute(
        "SELECT place_id, latitude, longitude FROM places WHERE content_type_id = 15"
    ).fetchall()

    for festival_id, lat, lon in festival_rows:
        related = conn.execute(
            """
            SELECT place_id, content_type_id, title, latitude, longitude
            FROM places
            WHERE place_id != ?
              AND content_type_id IN (12, 14, 28, 32, 38)
              AND latitude IS NOT NULL
              AND longitude IS NOT NULL
            ORDER BY ABS(latitude - ?) + ABS(longitude - ?) ASC
            LIMIT 8
            """,
            (festival_id, lat, lon),
        ).fetchall()

        for related_place_id, related_content_type_id, _, _, _ in related:
            conn.execute(
                """
                INSERT OR IGNORE INTO festival_related_places (
                    festival_id, related_place_id, related_content_type_id, distance_m, relation_reason
                ) VALUES (?, ?, ?, ?, 'nearby')
                """,
                (festival_id, related_place_id, related_content_type_id, None),
            )

    conn.commit()


def main():
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    region_id = 1

    import_places(conn, region_id)
    build_relationships(conn)

    conn.close()
    print(f"Created database: {DB_PATH}")


if __name__ == "__main__":
    main()
