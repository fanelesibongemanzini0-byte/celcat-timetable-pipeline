import csv, json
from collections import Counter, defaultdict
from pathlib import Path

RAW = Path("data/raw/modules")
OUT = Path("data/clean")
OUT.mkdir(parents=True, exist_ok=True)

def nullify(v):
    return None if v in (None, "", "[None]") else v.strip()

def parse_code(raw):
    main, _, note = raw.partition("-")
    parts = main.split("_")
    base = parts[0]
    section = parts[1] if len(parts) > 1 else None
    period = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
    return base, section, period, (note or None)

latest = sorted(RAW.glob("modules_*.json"))[-1]
mods = json.loads(latest.read_text())

rows = []
for m in mods:
    base, section, period, note = parse_code(m["code"])
    num = base[-3:]
    rows.append({
        "source_module_id": m["source_module_id"],
        "source_code": m["code"],
        "base_code": base,
        "prefix": base[0],
        "prefix_scheme": "digit" if base[0].isdigit() else "letter",
        "section": section,
        "period": period,
        "year_level": int(num[0]) if num.isdigit() else None,
        "title": nullify(m["title"]),
        "dept": nullify(m["dept"]),
        "faculty": nullify(m["faculty"]),
        "code_note": note,
    })

# Fill missing faculty from the most common faculty for that prefix
votes = defaultdict(Counter)
for r in rows:
    if r["faculty"]:
        votes[r["prefix"]][r["faculty"]] += 1
for r in rows:
    r["faculty_derived"] = False
    if not r["faculty"] and votes[r["prefix"]]:
        r["faculty"] = votes[r["prefix"]].most_common(1)[0][0]
        r["faculty_derived"] = True

out = OUT / "modules.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print(f"{len(rows)} rows → {out.resolve()}")
print("Faculty derived:", sum(r["faculty_derived"] for r in rows))
print("Still no faculty:", sum(1 for r in rows if not r["faculty"]))
print("Still no dept:", sum(1 for r in rows if not r["dept"]))