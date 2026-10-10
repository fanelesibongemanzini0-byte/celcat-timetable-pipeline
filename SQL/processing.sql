CREATE OR REPLACE VIEW tt.fact_module_sessions AS
SELECT o.class_id, o.week_no, o.class_date, o.duration_min, o.category,
       m.module_id, m.source_code, m.base_code, m.title,
       m.faculty, m.dept, m.year_level
FROM tt.class_occurrences o
JOIN tt.class_modules cm ON cm.class_id = o.class_id
JOIN tt.modules m        ON m.module_id = cm.module_id;


-- How many modules per faculty have at least one class?
SELECT m.faculty,
       COUNT(*) AS modules_in_catalogue,
       SUM(cm.module_id IS NOT NULL) AS modules_with_classes
FROM tt.modules m
LEFT JOIN (SELECT DISTINCT module_id FROM tt.class_modules) cm
       ON cm.module_id = m.module_id
GROUP BY m.faculty
ORDER BY modules_in_catalogue DESC;

-- Did any module labels from the events fail to match the module list?
SELECT COUNT(*) AS unmatched_items
FROM (SELECT DISTINCT TRIM(SUBSTRING_INDEX(item_text, ' (', 1)) AS code
      FROM tt_raw.event_resources
      WHERE resource_type = 'module') x
LEFT JOIN tt.modules m ON m.source_code = x.code
WHERE m.module_id IS NULL;

SELECT source_module_id, source_code, title
FROM tt.modules
WHERE faculty LIKE '%EDUCATION%'
LIMIT 3;

SELECT m.source_module_id, m.source_code, m.faculty,
       (SELECT COUNT(*) FROM tt_raw.events e
         WHERE e.source_module_id = m.source_module_id) AS raw_events,
       (SELECT COUNT(*) FROM tt.class_modules cm
         WHERE cm.module_id = m.module_id) AS clean_links
FROM tt.modules m
WHERE m.source_code = '3AW800_01_9';


SELECT source_module_id, source_code
FROM tt.modules
WHERE source_code = '3AW800_01_9';

SELECT v.venue_code, v.room_name, v.building_code, v.venue_type, v.capacity,
       COUNT(DISTINCT cv.class_id) AS classes,
       ROUND(SUM(o.duration_min) / 60, 1) AS hours_booked
FROM tt.venues v
JOIN tt.class_venues cv ON cv.venue_id = v.venue_id
JOIN tt.class_occurrences o ON o.class_id = cv.class_id
WHERE v.room_name LIKE '%HP1%'
GROUP BY v.venue_id, v.venue_code, v.room_name, v.building_code, v.venue_type, v.capacity;

SELECT COUNT(*) AS overlapping_pairs
FROM tt.fact_room_bookings a
JOIN tt.fact_room_bookings b
  ON a.venue_id = b.venue_id
 AND a.class_date = b.class_date
 AND a.class_id < b.class_id
 AND a.start_time < b.end_time
 AND b.start_time < a.end_time
WHERE a.room_name LIKE '%HP1%';

SELECT a.venue_code, COUNT(*) AS overlapping_pairs
FROM tt.fact_room_bookings a
JOIN tt.fact_room_bookings b
  ON a.venue_id = b.venue_id
 AND a.class_date = b.class_date
 AND a.class_id < b.class_id
 AND a.start_time < b.end_time
 AND b.start_time < a.end_time
GROUP BY a.venue_code
ORDER BY overlapping_pairs DESC
LIMIT 10;