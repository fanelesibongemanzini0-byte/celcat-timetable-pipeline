# extract_modules.py
import json, requests
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

BASE_URL = "http://mycelcat.unizulu.ac.za"  # same as settings.CELCAT_BASE_URL
RAW_DIR = Path("data/raw/modules")

def fetch_modules():
    resp = requests.get(f"{BASE_URL}/finder.xml", timeout=20)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    modules, seen = [], set()
    for r in root.findall("resource"):
        if r.get("type") != "module" or r.get("id") in seen:
            continue
        seen.add(r.get("id"))
        raw_name = (r.findtext("name") or "").strip()
        code, _, title = raw_name.partition(",")
        modules.append({
            "source_module_id": r.get("id"),
            "raw_name": raw_name,          # keep the untouched value
            "code": code.strip(),
            "title": title.strip(),
            "dept": r.findtext("dept"),
            "faculty": r.findtext("faculty"),
        })
    return modules

if __name__ == "__main__":
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = RAW_DIR / f"modules_{stamp}.json"
    mods = fetch_modules()
    out.write_text(json.dumps(mods, indent=2))
    print(f"Saved {len(mods)} modules → {out.resolve()}")