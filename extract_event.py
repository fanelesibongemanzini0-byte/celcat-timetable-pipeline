import json, time
from datetime import datetime, timezone
from pathlib import Path
import requests

BASE_URL = "http://mycelcat.unizulu.ac.za"
LIMIT = None         # set to None for the full run

mods = json.loads(sorted(Path("data/raw/modules").glob("modules_*.json"))[-1].read_text())
if LIMIT:
    mods = mods[:LIMIT]

stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
out = Path("data/raw/events") / stamp
out.mkdir(parents=True)

failed = []
with requests.Session() as s:
    for i, m in enumerate(mods, 1):
        mid = m["source_module_id"]
        try:
            r = s.get(f"{BASE_URL}/m{mid}.xml", timeout=20)
            r.raise_for_status()
            (out / f"m{mid}.xml").write_bytes(r.content)
        except requests.RequestException as e:
            failed.append({"id": mid, "status": getattr(e.response, "status_code", None), "error": str(e)})
        if i % 100 == 0:
            print(f"{i}/{len(mods)}")
        time.sleep(0.2)   # be polite to the university server

(out / "_failed.json").write_text(json.dumps(failed, indent=2))
print(f"Saved {len(mods) - len(failed)} files, {len(failed)} failed → {out.resolve()}")