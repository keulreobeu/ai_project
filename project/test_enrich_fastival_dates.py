import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from project import enrich_fastival_dates as enrich


class TourApiSyncTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.db_path = self.root / "test.db"
        self.snapshot_path = self.root / "api_snapshots" / "snapshot.json"

        schema_path = Path(__file__).with_name("seoul_festival_schema.sql")
        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.executescript(schema_path.read_text(encoding="utf-8"))
            connection.execute(
                """
                INSERT INTO places(
                    region_id, content_type_id, external_content_id, title
                ) VALUES (1, 15, 'festival-1', '테스트 행사')
                """
            )
            connection.commit()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_sync_saves_festival_course_steps_and_keyless_snapshot(self):
        course = {
            "contentid": "course-1",
            "contenttypeid": "25",
            "title": "테스트 여행코스",
            "addr1": "서울",
            "mapx": "126.9",
            "mapy": "37.5",
        }

        def fake_event(row, api_config, timeout):
            return {
                "place_id": row["place_id"],
                "content_id": row["external_content_id"],
                "event_start_date": "2026-07-01",
                "event_end_date": "2026-07-03",
                "raw": {
                    "contentid": row["external_content_id"],
                    "eventstartdate": "20260701",
                    "eventenddate": "20260703",
                },
            }

        def fake_course(course_item, api_config, timeout):
            return {
                "content_id": course_item["contentid"],
                "intro": {
                    "contentid": course_item["contentid"],
                    "distance": "5km",
                    "schedule": "1일",
                    "taketime": "3시간",
                    "theme": "도보",
                },
                "steps": [
                    {
                        "subcontentid": "step-1",
                        "subnum": "1",
                        "subname": "첫 장소",
                        "subdetailoverview": "첫 번째 코스",
                        "subdetailimg": "https://example.com/step.jpg",
                        "subdetailalt": "첫 장소 이미지",
                    }
                ],
            }

        raw_page = {
            "response": {
                "header": {"resultCode": "0000"},
                "body": {"totalCount": 1, "items": {"item": [course]}},
            }
        }
        with (
            patch.object(enrich, "get_api_config", return_value=("https://example.test", "secret-key")),
            patch.object(enrich, "fetch_event_detail", side_effect=fake_event),
            patch.object(
                enrich,
                "fetch_seoul_course_list",
                return_value=([course], [raw_page]),
            ),
            patch.object(enrich, "fetch_course_detail", side_effect=fake_course),
        ):
            counts = enrich.sync_tour_api(
                self.db_path, self.snapshot_path, workers=2, timeout=1
            )

        self.assertEqual(counts["festival_saved"], 1)
        self.assertEqual(counts["course_saved"], 1)
        self.assertEqual(counts["course_steps_saved"], 1)
        self.assertEqual(counts["failed"], 0)

        with closing(sqlite3.connect(self.db_path)) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT event_start_date, event_end_date FROM places "
                    "WHERE external_content_id = 'festival-1'"
                ).fetchone(),
                ("2026-07-01", "2026-07-03"),
            )
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM festival_details").fetchone()[0],
                1,
            )
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM travel_course_details").fetchone()[0],
                1,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT step_order, name FROM travel_course_steps"
                ).fetchone(),
                (1, "첫 장소"),
            )

        snapshot_text = self.snapshot_path.read_text(encoding="utf-8")
        snapshot = json.loads(snapshot_text)
        self.assertNotIn("secret-key", snapshot_text)
        self.assertFalse(snapshot["metadata"]["service_key_included"])
        self.assertEqual(len(snapshot["festival_details"]), 1)
        self.assertEqual(len(snapshot["course_details"]), 1)


if __name__ == "__main__":
    unittest.main()
