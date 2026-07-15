import argparse
import json
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = PROJECT_DIR.parent
DATA_DIR = REPOSITORY_ROOT / "data"
DB_PATH = PROJECT_DIR / "seoul_festival.db"
SNAPSHOT_PATH = PROJECT_DIR / "api_snapshots" / "tour_api_snapshot.json"
SEOUL_LEGAL_REGION_CODE = "11"
SEOUL_LEGACY_AREA_CODE = "1"
FESTIVAL_CONTENT_TYPE_ID = "15"
COURSE_CONTENT_TYPE_ID = "25"
FESTIVAL_DETAIL_FIELDS = (
    "agelimit",
    "bookingplace",
    "discountinfofestival",
    "eventenddate",
    "eventhomepage",
    "eventplace",
    "eventstartdate",
    "festivalgrade",
    "festivaltype",
    "placeinfo",
    "playtime",
    "program",
    "progresstype",
    "spendtimefestival",
    "sponsor1",
    "sponsor1tel",
    "sponsor2",
    "sponsor2tel",
    "subevent",
    "usetimefestival",
)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, data):
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary_path.replace(path)


def find_target_file(content_type_id):
    matches = []
    for path in DATA_DIR.rglob("*.json"):
        try:
            root = read_json(path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if (
            root.get("region") == "서울"
            and str(root.get("contentTypeId")) == str(content_type_id)
        ):
            matches.append(path)
    if len(matches) != 1:
        raise RuntimeError(
            f"서울 contentTypeId={content_type_id} 파일을 1개 찾을 수 없습니다: {matches}"
        )
    return matches[0]


def is_seoul(item):
    legal_region_code = str(item.get("lDongRegnCd") or "").strip()
    if legal_region_code:
        return legal_region_code == SEOUL_LEGAL_REGION_CODE

    address = str(item.get("addr1") or "").strip()
    if address.startswith("서울특별시") or address.startswith("서울 "):
        return True
    return str(item.get("areacode") or "").strip() == SEOUL_LEGACY_AREA_CODE


def ordered_merge(existing_items, merged_by_id):
    result = []
    seen = set()
    for existing in existing_items:
        content_id = str(existing.get("contentid") or "")
        merged = merged_by_id.get(content_id)
        if merged is None:
            continue
        result.append(merged)
        seen.add(content_id)

    new_items = [
        item for content_id, item in merged_by_id.items() if content_id not in seen
    ]
    new_items.sort(key=lambda item: (str(item.get("title") or ""), item["contentid"]))
    result.extend(new_items)
    return result


def load_festival_base_items(db_path):
    result = {}
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT p.external_content_id, p.source_data
            FROM places p
            JOIN regions r ON r.region_id = p.region_id
            WHERE p.content_type_id = 15 AND r.region_name = '서울'
            """
        ).fetchall()
    for content_id, source_data in rows:
        if not source_data:
            continue
        try:
            item = json.loads(source_data)
        except json.JSONDecodeError:
            continue
        result[str(content_id)] = item
    return result


def snapshot_course_list(snapshot):
    result = {}
    for payload in snapshot.get("course_list_pages", []):
        items = (
            payload.get("response", {})
            .get("body", {})
            .get("items", {})
            .get("item", [])
        )
        if isinstance(items, dict):
            items = [items]
        for item in items or []:
            content_id = str(item.get("contentid") or "")
            if content_id:
                result[content_id] = item
    return result


def merge_festivals(root, snapshot, db_path):
    existing_items = root.get("items", [])
    existing_by_id = {
        str(item.get("contentid") or ""): item for item in existing_items
    }
    database_by_id = load_festival_base_items(db_path)
    merged_by_id = {}
    rejected_non_seoul = 0

    for detail in snapshot.get("festival_details", []):
        raw = detail.get("raw") or {}
        content_id = str(detail.get("content_id") or raw.get("contentid") or "")
        base = existing_by_id.get(content_id) or database_by_id.get(content_id)
        if not content_id or not base or not is_seoul(base):
            rejected_non_seoul += 1
            continue
        detail_fields = {
            field: raw.get(field, "") for field in FESTIVAL_DETAIL_FIELDS
        }
        merged_by_id[content_id] = {**base, **detail_fields, **raw}

    items = ordered_merge(existing_items, merged_by_id)
    merged_root = {**root, "total": len(items), "items": items}
    stats = {
        "before": len(existing_items),
        "after": len(items),
        "added": len(set(merged_by_id) - set(existing_by_id)),
        "updated": len(set(merged_by_id) & set(existing_by_id)),
        "rejected_non_seoul": rejected_non_seoul,
    }
    return merged_root, stats


def merge_courses(root, snapshot):
    existing_items = root.get("items", [])
    existing_by_id = {
        str(item.get("contentid") or ""): item for item in existing_items
    }
    base_by_id = snapshot_course_list(snapshot)
    detail_by_id = {
        str(detail.get("content_id") or ""): detail
        for detail in snapshot.get("course_details", [])
        if detail.get("steps")
    }
    merged_by_id = {}
    rejected_non_seoul = 0
    excluded_without_course = 0

    for content_id, base in base_by_id.items():
        if not is_seoul(base):
            rejected_non_seoul += 1
            continue
        detail = detail_by_id.get(content_id)
        if detail is None:
            excluded_without_course += 1
            continue
        merged_by_id[content_id] = {
            **base,
            **(detail.get("intro") or {}),
            "courseSteps": detail["steps"],
        }

    items = ordered_merge(existing_items, merged_by_id)
    merged_root = {**root, "total": len(items), "items": items}
    stats = {
        "before": len(existing_items),
        "after": len(items),
        "added": len(set(merged_by_id) - set(existing_by_id)),
        "updated": len(set(merged_by_id) & set(existing_by_id)),
        "rejected_non_seoul": rejected_non_seoul,
        "excluded_without_course": excluded_without_course,
        "course_steps": sum(len(item["courseSteps"]) for item in items),
    }
    return merged_root, stats


def merge_tour_api_json(write=False):
    snapshot = read_json(SNAPSHOT_PATH)
    festival_path = find_target_file(FESTIVAL_CONTENT_TYPE_ID)
    course_path = find_target_file(COURSE_CONTENT_TYPE_ID)

    festival_root, festival_stats = merge_festivals(
        read_json(festival_path), snapshot, DB_PATH
    )
    course_root, course_stats = merge_courses(read_json(course_path), snapshot)

    if write:
        write_json(festival_path, festival_root)
        write_json(course_path, course_root)

    return {
        "festival_path": festival_path,
        "festival": festival_stats,
        "course_path": course_path,
        "course": course_stats,
        "written": write,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Merge ignored TourAPI snapshots into tracked Seoul JSON files."
    )
    parser.add_argument(
        "--write", action="store_true", help="write merged data to the target files"
    )
    args = parser.parse_args()
    result = merge_tour_api_json(write=args.write)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
