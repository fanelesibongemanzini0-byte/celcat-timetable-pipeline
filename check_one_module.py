import re
from pathlib import Path
import requests

BASE_URL = "http://mycelcat.unizulu.ac.za"
MODULE_ID = "9860"

# 1. the copy we saved on 8 October (the folder with the most files)
runs = sorted(Path("data/raw/events").glob("*"),
              key=lambda p: len(list(p.glob("m*.xml"))))
local = runs[-1] / f"m{MODULE_ID}.xml"
print("Saved copy:", local, "| exists:", local.exists())
if local.exists():
    txt = local.read_text(encoding="utf-8", errors="replace")
    print("  size:", len(txt), "| events:", len(re.findall(r"<event[ >]", txt)))

# 2. a fresh download right now
r = requests.get(f"{BASE_URL}/m{MODULE_ID}.xml", timeout=20)
print("Fresh download:", r.status_code, "| size:", len(r.text),
      "| events:", len(re.findall(r"<event[ >]", r.text)))