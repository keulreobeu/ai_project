-- Seoul tourism map service schema for SQLite
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS regions (
    region_id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS content_types (
    content_type_id INTEGER PRIMARY KEY,
    code_name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS places (
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
    event_start_date TEXT,
    event_end_date TEXT,
    UNIQUE(region_id, content_type_id, external_content_id),
    FOREIGN KEY (region_id) REFERENCES regions(region_id),
    FOREIGN KEY (content_type_id) REFERENCES content_types(content_type_id)
);

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

CREATE TABLE IF NOT EXISTS festival_related_places (
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

CREATE TABLE IF NOT EXISTS posts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    edit_password TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
);

CREATE INDEX IF NOT EXISTS idx_places_region_type ON places(region_id, content_type_id);
CREATE INDEX IF NOT EXISTS idx_places_title ON places(title);
CREATE INDEX IF NOT EXISTS idx_places_geo ON places(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_related_festival ON festival_related_places(festival_id);
CREATE INDEX IF NOT EXISTS idx_related_type ON festival_related_places(related_content_type_id);
CREATE INDEX IF NOT EXISTS idx_course_steps_course ON travel_course_steps(course_id, step_order);
CREATE INDEX IF NOT EXISTS idx_posts_region_created ON posts(region_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_title ON posts(title);

INSERT OR IGNORE INTO regions(region_name) VALUES ('서울');

INSERT OR IGNORE INTO content_types(content_type_id, code_name, display_name) VALUES
(12, 'tourist_attraction', '관광지'),
(14, 'culture_facility', '문화시설'),
(15, 'festival_event', '축제공연행사'),
(25, 'travel_course', '여행코스'),
(28, 'leports', '레포츠'),
(32, 'accommodation', '숙박'),
(38, 'shopping', '쇼핑');
