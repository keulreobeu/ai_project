-- Seoul festival map service schema for SQLite
-- 목적: 축제/공연/행사 목록 조회 + 축제 선택 시 주변 관광지/숙박/레포츠/문화시설/쇼핑 지도 표시

PRAGMA foreign_keys = ON;

CREATE TABLE regions (
    region_id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT NOT NULL UNIQUE
);

CREATE TABLE content_types (
    content_type_id INTEGER PRIMARY KEY,
    code_name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL
);

CREATE TABLE places (
    place_id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_id INTEGER NOT NULL,
    content_type_id INTEGER NOT NULL,
    external_content_id TEXT NOT NULL,
    title TEXT NOT NULL,
    address1 TEXT,
    address2 TEXT,
    zipcode TEXT,
    tel TEXT,
    latitude REAL,
    longitude REAL,
    thumbnail_url TEXT,
    image_url TEXT,
    map_level TEXT,
    source_data TEXT,
    created_at TEXT,
    updated_at TEXT,
    UNIQUE(region_id, content_type_id, external_content_id),
    FOREIGN KEY (region_id) REFERENCES regions(region_id),
    FOREIGN KEY (content_type_id) REFERENCES content_types(content_type_id)
);

CREATE TABLE festival_related_places (
    festival_id INTEGER NOT NULL,
    related_place_id INTEGER NOT NULL,
    related_content_type_id INTEGER NOT NULL,
    distance_m INTEGER,
    relation_reason TEXT NOT NULL DEFAULT 'nearby',
    PRIMARY KEY (festival_id, related_place_id),
    FOREIGN KEY (festival_id) REFERENCES places(place_id),
    FOREIGN KEY (related_place_id) REFERENCES places(place_id),
    FOREIGN KEY (related_content_type_id) REFERENCES content_types(content_type_id)
);

CREATE INDEX idx_places_region_type ON places(region_id, content_type_id);
CREATE INDEX idx_places_title ON places(title);
CREATE INDEX idx_places_geo ON places(latitude, longitude);
CREATE INDEX idx_related_festival ON festival_related_places(festival_id);
CREATE INDEX idx_related_type ON festival_related_places(related_content_type_id);

-- 기본 분류값 seed
INSERT INTO regions(region_name) VALUES ('서울');

INSERT INTO content_types(content_type_id, code_name, display_name) VALUES
(12, 'tourist_attraction', '관광지'),
(14, 'culture_facility', '문화시설'),
(15, 'festival_event', '축제공연행사'),
(28, 'leports', '레포츠'),
(32, 'accommodation', '숙박'),
(38, 'shopping', '쇼핑');
