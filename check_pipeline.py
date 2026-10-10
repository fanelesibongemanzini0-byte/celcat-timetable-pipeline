import csv, re
from datetime import datetime
from pathlib import Path

runs = sorted(Path("data/raw/events").glob("*"),
              key=lambda p: len(list(p.glob("m*.xml"))))
run = runs[-1]
files = list(run.glob("m*.xml"))
print("Run folder:", run.name, "| XML files:", len(files))

with_events = {
    f.stem[1:] for f in files
    if re.search(r"<event[ >]", f.read_text(encoding="utf-8", errors="replace"))
}
print("XML files that contain events:", len(with_events))

csv_path = Path("data/clean/events.csv")
rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
in_csv = {r["source_module_id"] for r in rows}
print("events.csv rows:", len(rows), "| modules in events.csv:", len(in_csv))
print("events.csv last modified:", datetime.fromtimestamp(csv_path.stat().st_mtime))

print("Module 9860 has events in XML:", "9860" in with_events,
      "| is in events.csv:", "9860" in in_csv)
missing = sorted(with_events - in_csv)
print("Modules with events in XML but missing from events.csv:", len(missing), missing[:10])