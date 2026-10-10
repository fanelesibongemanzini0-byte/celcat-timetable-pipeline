import csv
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

run = sorted(Path("data/raw/events").glob("*"))[-1]
if not (run / "_failed.json").exists():
    raise SystemExit("Extract not finished for this run - wait for 'Saved ... files' and try again.")
events, resources = [], []

for f in sorted(run.glob("m*.xml")):
    mod_id = f.stem[1:]
    root = ET.parse(f).getroot()
    sub = root.findtext("option/subheading")
    for ev in root.findall("event"):
        eid = ev.get("id")
        events.append({
            "event_id": eid, "source_module_id": mod_id, "subheading": sub,
            "day_index": ev.findtext("day"),
            "start_time": ev.findtext("starttime"),
            "end_time": ev.findtext("endtime"),
            "pretty_times": ev.findtext("prettytimes"),
            "category": ev.findtext("category"),
            "pretty_weeks": ev.findtext("prettyweeks"),
            "raw_weeks": ev.findtext("rawweeks"),
        })
        res = ev.find("resources")
        if res is not None:
            for r in res:
                for item in r.findall("item"):
                    a = item.find("a")
                    text = a.text if a is not None and a.text else item.text
                    resources.append({
                        "event_id": eid, "source_module_id": mod_id,
                        "resource_type": r.tag, "item_text": (text or "").strip(),
                    })

out = Path("data/clean"); out.mkdir(parents=True, exist_ok=True)
for name, rows in [("events", events), ("event_resources", resources)]:
    if rows:
        with open(out / f"{name}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=rows[0].keys())
            w.writeheader(); w.writerows(rows)

print(f"Run folder: {run.name} | files: {len(list(run.glob('m*.xml')))}")
print(f"Event rows: {len(events)} | distinct event ids: {len({e['event_id'] for e in events})}")
print("Resource types:", Counter(r["resource_type"] for r in resources))
print("Categories:", Counter(e["category"] for e in events).most_common(8))
print("raw_weeks lengths:", Counter(len(e["raw_weeks"] or "") for e in events))

multi = Counter((r["event_id"], r["source_module_id"], r["resource_type"]) for r in resources)
print("Events with >1 room:", sum(1 for k, n in multi.items() if k[2] == "room" and n > 1))
print("Events with >1 staff:", sum(1 for k, n in multi.items() if k[2] == "staff" and n > 1))
print("Sample:", events[:2])