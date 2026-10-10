SET SQL_SAFE_UPDATES = 0;

-- Reset so the script is safe to re-run
DELETE FROM tt.class_venues;
DELETE FROM tt.class_modules;
DELETE FROM tt.classes;
DELETE FROM tt.venues;
DELETE FROM tt.modules;

-- 1. MODULES
INSERT INTO tt.modules
  (source_module_id, source_code, base_code, prefix_scheme, section,
   period_code, year_level, title, dept, faculty, faculty_derived)
SELECT source_module_id, source_code, base_code, prefix_scheme, section,
       CAST(`period` AS UNSIGNED), CAST(year_level AS UNSIGNED),
       title, dept, faculty, (faculty_derived = 'True')
FROM tt_raw.modules;

-- 2. CLASSES (one row per CELCAT event id; shared events appear in several files)
INSERT INTO tt.classes
  (class_id, day_index, start_time, end_time, category, pretty_weeks, raw_weeks)
SELECT CAST(event_id AS UNSIGNED),
       MIN(CAST(day_index AS UNSIGNED)),
       MIN(CAST(start_time AS TIME)),
       MIN(CAST(end_time AS TIME)),
       MIN(category), MIN(pretty_weeks), MIN(raw_weeks)
FROM tt_raw.events
GROUP BY event_id;

-- 3. VENUES (parse '1217_2_AL 12 (LECTURE THEATER  [Capacity: 75])')
INSERT INTO tt.venues
  (venue_code, building_code, level_code, room_name, venue_type, capacity)
WITH r AS (
  SELECT DISTINCT item_text,
         TRIM(SUBSTRING_INDEX(item_text, ' (', 1)) AS venue_code
  FROM tt_raw.event_resources
  WHERE resource_type = 'room' AND item_text IS NOT NULL AND item_text <> ''
)
SELECT venue_code,
       MIN(CASE WHEN venue_code REGEXP '^[^_]+_[^_]+_.+'
                THEN SUBSTRING_INDEX(venue_code, '_', 1) END),
       MIN(CASE WHEN venue_code REGEXP '^[^_]+_[^_]+_.+'
                THEN SUBSTRING_INDEX(SUBSTRING_INDEX(venue_code, '_', 2), '_', -1) END),
       MIN(CASE WHEN venue_code REGEXP '^[^_]+_[^_]+_.+'
                THEN SUBSTRING(venue_code, LENGTH(SUBSTRING_INDEX(venue_code, '_', 2)) + 2)
                ELSE venue_code END),
       MIN(CASE WHEN item_text LIKE '% (%'
                THEN TRIM(TRAILING ')' FROM
                     TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(item_text, ' (', -1), '[', 1)))
           END),
       MAX(CAST(REGEXP_SUBSTR(REGEXP_SUBSTR(item_text, 'Capacity: [0-9]+'), '[0-9]+') AS UNSIGNED))
FROM r
GROUP BY venue_code;

-- 4. CLASS ↔ MODULE
INSERT INTO tt.class_modules (class_id, module_id)
SELECT DISTINCT CAST(r.event_id AS UNSIGNED), m.module_id
FROM tt_raw.event_resources r
JOIN tt.modules m ON m.source_code = TRIM(SUBSTRING_INDEX(r.item_text, ' (', 1))
WHERE r.resource_type = 'module';

-- 5. CLASS ↔ VENUE
INSERT INTO tt.class_venues (class_id, venue_id)
SELECT DISTINCT CAST(r.event_id AS UNSIGNED), v.venue_id
FROM tt_raw.event_resources r
JOIN tt.venues v ON v.venue_code = TRIM(SUBSTRING_INDEX(r.item_text, ' (', 1))
WHERE r.resource_type = 'room';

-- CHECKS
SELECT 'modules' AS tbl, COUNT(*) AS n FROM tt.modules
UNION ALL SELECT 'classes', COUNT(*) FROM tt.classes
UNION ALL SELECT 'venues', COUNT(*) FROM tt.venues
UNION ALL SELECT 'class_modules', COUNT(*) FROM tt.class_modules
UNION ALL SELECT 'class_venues', COUNT(*) FROM tt.class_venues;

SELECT COUNT(*) AS module_items_unmatched
FROM (SELECT DISTINCT event_id, TRIM(SUBSTRING_INDEX(item_text, ' (', 1)) AS code
      FROM tt_raw.event_resources WHERE resource_type = 'module') x
LEFT JOIN tt.modules m ON m.source_code = x.code
WHERE m.module_id IS NULL;

SELECT COUNT(*) AS classes_without_module
FROM tt.classes c
LEFT JOIN tt.class_modules cm ON cm.class_id = c.class_id
WHERE cm.class_id IS NULL;

SELECT * FROM weeks;

SELECT MIN(start_time) AS earliest, MAX(end_time) AS latest, MAX(day_index) AS last_day FROM tt.classes;