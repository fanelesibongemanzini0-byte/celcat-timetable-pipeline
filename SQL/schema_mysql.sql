CREATE DATABASE IF NOT EXISTS tt_raw CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS tt     CHARACTER SET utf8mb4;

-- RAW: CSVs exactly as produced, all text
CREATE TABLE IF NOT EXISTS tt_raw.modules (
    source_module_id TEXT, source_code TEXT, base_code TEXT, prefix TEXT,
    prefix_scheme TEXT, section TEXT, `period` TEXT, year_level TEXT, title TEXT,
    dept TEXT, faculty TEXT, code_note TEXT, faculty_derived TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS tt_raw.events (
    event_id TEXT, source_module_id TEXT, subheading TEXT, day_index TEXT,
    start_time TEXT, end_time TEXT, pretty_times TEXT, category TEXT,
    pretty_weeks TEXT, raw_weeks TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS tt_raw.event_resources (
    event_id TEXT, source_module_id TEXT, resource_type TEXT, item_text TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CLEAN MODEL
CREATE TABLE IF NOT EXISTS tt.modules (
    module_id        INT AUTO_INCREMENT PRIMARY KEY,
    source_module_id VARCHAR(20)  NOT NULL UNIQUE,
    source_code      VARCHAR(60)  NOT NULL,
    base_code        VARCHAR(20)  NOT NULL,
    prefix_scheme    VARCHAR(10),
    section          VARCHAR(5),
    period_code      INT,
    year_level       INT,
    title            VARCHAR(255),
    dept             VARCHAR(150),
    faculty          VARCHAR(150),
    faculty_derived  BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS tt.venues (
    venue_id      INT AUTO_INCREMENT PRIMARY KEY,
    venue_code    VARCHAR(100) NOT NULL UNIQUE,
    building_code VARCHAR(20),
    level_code    VARCHAR(5),
    room_name     VARCHAR(60),
    venue_type    VARCHAR(80),
    capacity      INT
);

CREATE TABLE IF NOT EXISTS tt.classes (
    class_id     INT PRIMARY KEY,
    day_index    TINYINT NOT NULL,
    start_time   TIME NOT NULL,
    end_time     TIME NOT NULL,
    category     VARCHAR(10),
    pretty_weeks VARCHAR(60),
    raw_weeks    VARCHAR(60) NOT NULL
);

CREATE TABLE IF NOT EXISTS tt.class_modules (
    class_id  INT NOT NULL,
    module_id INT NOT NULL,
    PRIMARY KEY (class_id, module_id),
    FOREIGN KEY (class_id)  REFERENCES tt.classes(class_id),
    FOREIGN KEY (module_id) REFERENCES tt.modules(module_id)
);

CREATE TABLE IF NOT EXISTS tt.class_venues (
    class_id INT NOT NULL,
    venue_id INT NOT NULL,
    PRIMARY KEY (class_id, venue_id),
    FOREIGN KEY (class_id) REFERENCES tt.classes(class_id),
    FOREIGN KEY (venue_id) REFERENCES tt.venues(venue_id)
);

CREATE TABLE IF NOT EXISTS tt.weeks (
    week_no    TINYINT PRIMARY KEY,
    week_start DATE NOT NULL
);

-- Week 1 starts Monday 2026-07-06 (confirmed across all 1,251 module files)
INSERT IGNORE INTO tt.weeks (week_no, week_start)
WITH RECURSIVE n AS (SELECT 1 AS i UNION ALL SELECT i + 1 FROM n WHERE i < 52)
SELECT i, DATE_ADD('2026-07-06', INTERVAL 7 * (i - 1) DAY) FROM n;

-- VIEWS
CREATE OR REPLACE VIEW tt.class_occurrences AS
SELECT c.class_id,
       w.week_no,
       DATE_ADD(w.week_start, INTERVAL c.day_index DAY) AS class_date,
       c.start_time,
       c.end_time,
       TIME_TO_SEC(TIMEDIFF(c.end_time, c.start_time)) DIV 60 AS duration_min,
       c.category
FROM tt.classes c
JOIN tt.weeks w
  ON SUBSTRING(c.raw_weeks, w.week_no, 1) = 'Y';

CREATE OR REPLACE VIEW tt.fact_room_bookings AS
SELECT o.class_id, o.week_no, o.class_date,
       DAYNAME(o.class_date)      AS weekday,
       WEEKDAY(o.class_date) + 1  AS weekday_no,
       HOUR(o.start_time)         AS start_hour,
       o.start_time, o.end_time, o.duration_min, o.category,
       v.venue_id, v.venue_code, v.room_name, v.building_code,
       v.venue_type, v.capacity
FROM tt.class_occurrences o
JOIN tt.class_venues cv ON cv.class_id = o.class_id
JOIN tt.venues v        ON v.venue_id  = cv.venue_id;

CREATE OR REPLACE VIEW tt.fact_module_sessions AS
SELECT o.class_id, o.week_no, o.class_date, o.duration_min, o.category,
       m.module_id, m.source_code, m.base_code, m.title,
       m.faculty, m.dept, m.year_level
FROM tt.class_occurrences o
JOIN tt.class_modules cm ON cm.class_id = o.class_id
JOIN tt.modules m        ON m.module_id = cm.module_id;