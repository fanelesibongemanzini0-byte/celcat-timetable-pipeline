import csv
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

clean = Path("data/clean")
events = list(csv.DictReader(open(clean / "events.csv", encoding="utf-8")))
res = list(csv.DictReader(open(clean / "event_resources.csv", encoding="utf-8")))

by_id = defaultdict(set)
for e in events:
    by_id[e["event_id"]].add(e["source_module_id"])
shared = {k: v for k, v in by_id.items() if len(v) > 1}
print(f"Event ids: {len(by_id)} | appearing in >1 module file: {len(shared)}")

seen, diff = {}, 0
for e in events:
    k = (e["day_index"], e["start_time"], e["end_time"], e["raw_weeks"])
    if e["event_id"] in seen and seen[e["event_id"]] != k:
        diff += 1
    seen.setdefault(e["event_id"], k)
print("Same id but different day/time/weeks:", diff)

mod_items, rooms = defaultdict(set), defaultdict(set)
for r in res:
    if r["resource_type"] == "module":
        mod_items[r["event_id"]].add(r["item_text"])
    elif r["resource_type"] == "room":
        rooms[r["event_id"]].add(r["item_text"])

multi = {k: v for k, v in mod_items.items() if len(v) > 1}
print(f"\nEvents listing >1 module: {len(multi)}")
for k, v in list(multi.items())[:3]:
    print("  ", k, sorted(v))

print("Events with no room:", sum(1 for k in by_id if not rooms.get(k)))
print("Events with >1 room:", sum(1 for v in rooms.values() if len(v) > 1))
print("Room samples:", Counter(t for v in rooms.values() for t in v).most_common(15))
print("Categories:", Counter(e["category"] for e in events))
print("Resource types:", Counter(r["resource_type"] for r in res))

run = sorted(Path("data/raw/events").glob("*"))[-1]
root = ET.parse(sorted(run.glob("m*.xml"))[0]).getroot()
print("\nRoot:", root.tag, root.attrib)
seen_tags = set()
for child in root:
    if child.tag == "event" or child.tag in seen_tags:
        continue
    seen_tags.add(child.tag)
    print(ET.tostring(child, encoding="unicode")[:500].strip())