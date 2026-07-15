import json
import os
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = PROJECT_DIR.parent
DB_PATH = PROJECT_DIR / "seoul_festival.db"
ENV_PATH = REPOSITORY_ROOT / "backend" / ".env"
SNAPSHOT_PATH = PROJECT_DIR / "api_snapshots" / "tour_api_snapshot.json"
DEFAULT_ENDPOINT = "https://apis.data.go.kr/B551011/KorService2"
SEOUL_LEGAL_REGION_CODE = "11"
FESTIVAL_CONTENT_TYPE_ID = 15
COURSE_CONTENT_TYPE_ID = 25


def load_local_env(path=ENV_PATH):
    """Load the ignored local .env file without overriding shell variables."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ.setdefault(name, value)


def get_api_config():
    load_local_env()
    endpoint = os.getenv("DATA_GO_KR_ENDPOINT", DEFAULT_ENDPOINT).strip().rstrip("/")

    service_key = os.getenv("DATA_GO_KR_SERVICE_KEY_DECODED", "").strip()
    if not service_key:
        encoded_key = os.getenv("DATA_GO_KR_SERVICE_KEY_ENCODED", "").strip()
        if encoded_key:
            service_key = urllib.parse.unquote(encoded_key)
    if not service_key:
        service_key = (
            os.getenv("TOURAPI_SERVICE_KEY", "").strip()
            or os.getenv("SERVICE_KEY", "").strip()
        )
    if not service_key:
        raise RuntimeError(
            f"공공데이터 API 키가 없습니다. {ENV_PATH}에 "
            "DATA_GO_KR_SERVICE_KEY_DECODED를 설정하세요."
        )
    return endpoint, service_key


def request_json(endpoint, service_key, operation, params=None, timeout=15):
    query = {
        "serviceKey": service_key,
        "MobileOS": "ETC",
        "MobileApp": "LocalHub",
        "_type": "json",
        **(params or {}),
    }
    url = f"{endpoint}/{operation}?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "LocalHub/1.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        # The URL contains the service key, so never include it in the error.
        raise RuntimeError(f"TourAPI {operation} 호출 실패: {error}") from error

    api_response = payload.get("response", {})
    header = api_response.get("header", {})
    result_code = str(header.get("resultCode", ""))
    if result_code and result_code != "0000":
        result_message = header.get("resultMsg", "알 수 없는 오류")
        raise RuntimeError(f"TourAPI {operation} 오류 {result_code}: {result_message}")
    return payload


def response_items(payload):
    items = payload.get("response", {}).get("body", {}).get("items", {})
    if not items:
        return []
    result = items.get("item", [])
    if isinstance(result, dict):
        return [result]
    return result or []


def normalize_date(value):
    if not value:
        return None
    text = str(value).strip()
    if len(text) == 8 and text.isdigit():
        return f"{text[0:4]}-{text[4:6]}-{text[6:8]}"
    return text


def fetch_event_detail(row, api_config, timeout=15):
    endpoint, service_key = api_config
    payload = request_json(
        endpoint,
        service_key,
        "detailIntro2",
        {
            "contentId": row["external_content_id"],
            "contentTypeId": row["content_type_id"],
        },
        timeout,
    )
    items = response_items(payload)
    item = items[0] if items else {}
    return {
        "place_id": row["place_id"],
        "content_id": row["external_content_id"],
        "event_start_date": normalize_date(
            item.get("eventstartdate") or item.get("eventStartDate")
        ),
        "event_end_date": normalize_date(
            item.get("eventenddate") or item.get("eventEndDate")
        ),
        "raw": item,
    }


def fetch_seoul_course_list(api_config, timeout=15):
    endpoint, service_key = api_config
    page = 1
    all_items = []
    raw_pages = []

    while True:
        payload = request_json(
            endpoint,
            service_key,
            "areaBasedList2",
            {
                "numOfRows": 100,
                "pageNo": page,
                "arrange": "A",
                "contentTypeId": COURSE_CONTENT_TYPE_ID,
                "lDongRegnCd": SEOUL_LEGAL_REGION_CODE,
            },
            timeout,
        )
        items = response_items(payload)
        all_items.extend(items)
        raw_pages.append(payload)

        body = payload.get("response", {}).get("body", {})
        total_count = int(body.get("totalCount") or 0)
        if not items or len(all_items) >= total_count:
            break
        page += 1

    return all_items, raw_pages


def fetch_course_detail(course, api_config, timeout=15):
    endpoint, service_key = api_config
    content_id = str(course["contentid"])
    common = {
        "contentId": content_id,
        "contentTypeId": COURSE_CONTENT_TYPE_ID,
    }
    intro_payload = request_json(
        endpoint, service_key, "detailIntro2", common, timeout
    )
    steps_payload = request_json(
        endpoint,
        service_key,
        "detailInfo2",
        {**common, "numOfRows": 100, "pageNo": 1},
        timeout,
    )
    intro_items = response_items(intro_payload)
    return {
        "content_id": content_id,
        "intro": intro_items[0] if intro_items else {},
        "steps": response_items(steps_payload),
    }


def ensure_database_schema(connection):
    place_columns = {
        row[1] for row in connection.execute("PRAGMA table_info(places)").fetchall()
    }
    if "event_start_date" not in place_columns:
        connection.execute("ALTER TABLE places ADD COLUMN event_start_date TEXT")
    if "event_end_date" not in place_columns:
        connection.execute("ALTER TABLE places ADD COLUMN event_end_date TEXT")

    connection.execute(
        """
        INSERT OR IGNORE INTO content_types(content_type_id, code_name, display_name)
        VALUES (25, 'travel_course', '여행코스')
        """
    )
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS festival_details (
            festival_id INTEGER PRIMARY KEY,
            event_start_date TEXT,
            event_end_date TEXT,
            source_data TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            FOREIGN KEY (festival_id) REFERENCES places(place_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS travel_course_details (
            course_id INTEGER PRIMARY KEY,
            distance TEXT,
            schedule TEXT,
            duration TEXT,
            theme TEXT,
            source_data TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            FOREIGN KEY (course_id) REFERENCES places(place_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS travel_course_steps (
            course_id INTEGER NOT NULL,
            step_order INTEGER NOT NULL,
            external_subcontent_id TEXT,
            name TEXT,
            overview TEXT,
            image_url TEXT,
            image_alt TEXT,
            source_data TEXT NOT NULL,
            PRIMARY KEY (course_id, step_order),
            FOREIGN KEY (course_id) REFERENCES places(place_id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_course_steps_course
        ON travel_course_steps(course_id, step_order);
        """
    )


def save_event_result(connection, result, fetched_at):
    connection.execute(
        """
        UPDATE places
        SET event_start_date = COALESCE(?, event_start_date),
            event_end_date = COALESCE(?, event_end_date)
        WHERE place_id = ?
        """,
        (
            result["event_start_date"],
            result["event_end_date"],
            result["place_id"],
        ),
    )
    connection.execute(
        """
        INSERT INTO festival_details(
            festival_id, event_start_date, event_end_date, source_data, fetched_at
        ) VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(festival_id) DO UPDATE SET
            event_start_date = excluded.event_start_date,
            event_end_date = excluded.event_end_date,
            source_data = excluded.source_data,
            fetched_at = excluded.fetched_at
        """,
        (
            result["place_id"],
            result["event_start_date"],
            result["event_end_date"],
            json.dumps(result["raw"], ensure_ascii=False),
            fetched_at,
        ),
    )


def upsert_course_places(connection, courses):
    region_row = connection.execute(
        "SELECT region_id FROM regions WHERE region_name = '서울'"
    ).fetchone()
    if region_row is None:
        raise RuntimeError("regions 테이블에 서울 지역이 없습니다.")
    region_id = region_row[0]

    for item in courses:
        connection.execute(
            """
            INSERT INTO places(
                region_id, content_type_id, external_content_id, title,
                address1, address2, zipcode, tel, latitude, longitude,
                thumbnail_url, image_url, map_level, source_data,
                created_at, updated_at
            ) VALUES (?, 25, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(region_id, content_type_id, external_content_id) DO UPDATE SET
                title = excluded.title,
                address1 = excluded.address1,
                address2 = excluded.address2,
                zipcode = excluded.zipcode,
                tel = excluded.tel,
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                thumbnail_url = excluded.thumbnail_url,
                image_url = excluded.image_url,
                map_level = excluded.map_level,
                source_data = excluded.source_data,
                updated_at = excluded.updated_at
            """,
            (
                region_id,
                str(item["contentid"]),
                item.get("title") or "제목 없음",
                item.get("addr1"),
                item.get("addr2"),
                item.get("zipcode"),
                item.get("tel"),
                item.get("mapy"),
                item.get("mapx"),
                item.get("firstimage2"),
                item.get("firstimage"),
                item.get("mlevel"),
                json.dumps(item, ensure_ascii=False),
                item.get("createdtime"),
                item.get("modifiedtime"),
            ),
        )


def save_course_result(connection, result, fetched_at):
    course_row = connection.execute(
        """
        SELECT place_id FROM places
        WHERE content_type_id = 25 AND external_content_id = ?
        """,
        (result["content_id"],),
    ).fetchone()
    if course_row is None:
        raise RuntimeError(f"여행코스 부모 레코드가 없습니다: {result['content_id']}")
    course_id = course_row[0]
    intro = result["intro"]

    connection.execute(
        """
        INSERT INTO travel_course_details(
            course_id, distance, schedule, duration, theme, source_data, fetched_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(course_id) DO UPDATE SET
            distance = excluded.distance,
            schedule = excluded.schedule,
            duration = excluded.duration,
            theme = excluded.theme,
            source_data = excluded.source_data,
            fetched_at = excluded.fetched_at
        """,
        (
            course_id,
            intro.get("distance"),
            intro.get("schedule"),
            intro.get("taketime"),
            intro.get("theme"),
            json.dumps(intro, ensure_ascii=False),
            fetched_at,
        ),
    )
    connection.execute(
        "DELETE FROM travel_course_steps WHERE course_id = ?", (course_id,)
    )
    for fallback_order, step in enumerate(result["steps"], 1):
        raw_order = step.get("subnum")
        try:
            step_order = int(raw_order)
        except (TypeError, ValueError):
            step_order = fallback_order
        connection.execute(
            """
            INSERT OR REPLACE INTO travel_course_steps(
                course_id, step_order, external_subcontent_id, name, overview,
                image_url, image_alt, source_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                course_id,
                step_order,
                step.get("subcontentid"),
                step.get("subname"),
                step.get("subdetailoverview"),
                step.get("subdetailimg"),
                step.get("subdetailalt"),
                json.dumps(step, ensure_ascii=False),
            ),
        )


def write_snapshot(snapshot, path=SNAPSHOT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    temporary_path.replace(path)


def sync_tour_api(db_path=DB_PATH, snapshot_path=SNAPSHOT_PATH, workers=4, timeout=15):
    api_config = get_api_config()
    fetched_at = datetime.now(timezone.utc).isoformat()
    snapshot = {
        "metadata": {
            "fetched_at": fetched_at,
            "endpoint": api_config[0],
            "region": "서울",
            "service_key_included": False,
        },
        "festival_details": [],
        "course_list_pages": [],
        "course_details": [],
        "errors": [],
    }
    counts = {
        "festival_total": 0,
        "festival_saved": 0,
        "course_total": 0,
        "course_saved": 0,
        "course_steps_saved": 0,
        "failed": 0,
    }

    with closing(sqlite3.connect(db_path)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        ensure_database_schema(connection)
        connection.commit()

        festival_rows = connection.execute(
            """
            SELECT place_id, external_content_id, content_type_id
            FROM places
            WHERE content_type_id = 15 AND external_content_id IS NOT NULL
            ORDER BY place_id
            """
        ).fetchall()
        counts["festival_total"] = len(festival_rows)
        print(f"행사 상세 조회 시작: {len(festival_rows)}건")

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(fetch_event_detail, row, api_config, timeout): row
                for row in festival_rows
            }
            for processed, future in enumerate(as_completed(futures), 1):
                row = futures[future]
                try:
                    result = future.result()
                    save_event_result(connection, result, fetched_at)
                    snapshot["festival_details"].append(result)
                    counts["festival_saved"] += 1
                except Exception as error:
                    counts["failed"] += 1
                    snapshot["errors"].append(
                        {
                            "operation": "detailIntro2",
                            "content_id": row["external_content_id"],
                            "error": str(error),
                        }
                    )
                if processed % 10 == 0 or processed == len(festival_rows):
                    connection.commit()
                    write_snapshot(snapshot, snapshot_path)
                    print(
                        f"행사 진행: {processed}/{len(festival_rows)} "
                        f"(저장 {counts['festival_saved']}, 실패 {counts['failed']})"
                    )

        print("서울 여행코스 목록 조회 시작")
        courses, raw_pages = fetch_seoul_course_list(api_config, timeout)
        snapshot["course_list_pages"] = raw_pages
        counts["course_total"] = len(courses)
        upsert_course_places(connection, courses)
        connection.commit()
        write_snapshot(snapshot, snapshot_path)
        print(f"여행코스 목록 저장: {len(courses)}건")

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(fetch_course_detail, course, api_config, timeout): course
                for course in courses
            }
            for processed, future in enumerate(as_completed(futures), 1):
                course = futures[future]
                try:
                    result = future.result()
                    save_course_result(connection, result, fetched_at)
                    snapshot["course_details"].append(result)
                    counts["course_saved"] += 1
                    counts["course_steps_saved"] += len(result["steps"])
                except Exception as error:
                    counts["failed"] += 1
                    snapshot["errors"].append(
                        {
                            "operation": "course detailIntro2/detailInfo2",
                            "content_id": str(course.get("contentid", "")),
                            "error": str(error),
                        }
                    )
                if processed % 10 == 0 or processed == len(courses):
                    connection.commit()
                    write_snapshot(snapshot, snapshot_path)
                    print(
                        f"코스 상세 진행: {processed}/{len(courses)} "
                        f"(저장 {counts['course_saved']}, 실패 {counts['failed']})"
                    )

    write_snapshot(snapshot, snapshot_path)
    return counts


def main():
    counts = sync_tour_api()
    print(
        "TourAPI 동기화 완료: "
        f"행사 {counts['festival_saved']}/{counts['festival_total']}건, "
        f"여행코스 {counts['course_saved']}/{counts['course_total']}건, "
        f"코스 단계 {counts['course_steps_saved']}건, "
        f"실패 {counts['failed']}건"
    )
    print(f"원본 JSON: {SNAPSHOT_PATH}")


if __name__ == "__main__":
    main()
