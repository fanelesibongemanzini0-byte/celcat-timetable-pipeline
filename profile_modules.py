import json
from pathlib import Path
from collections import Counter

latest = sorted(Path("data/raw/modules").glob("modules_*.json"))[-1]
mods = json.loads(latest.read_text())
print(f"File: {latest.name} | rows: {len(mods)}")

# 1. Missing values per field
for field in ["code", "title", "dept", "faculty"]:
    missing = sum(1 for m in mods if not m[field])
    print(f"{field:8} missing: {missing}")

# 2. Duplicate codes (same code, different CELCAT id)
codes = Counter(m["code"] for m in mods)
dupes = {c: n for c, n in codes.items() if n > 1}
print(f"\nDuplicate codes: {len(dupes)}")
print(list(dupes.items())[:5])

# 3. Faculty / dept spread
print("\nFaculties:", Counter(m["faculty"] for m in mods).most_common(10))
print("Depts:", Counter(m["dept"] for m in mods).most_common(10))

# 4. Codes that don't fit the pattern (digit + letters + digits, e.g. 1CSC111)
import re
odd = [m["code"] for m in mods if not re.fullmatch(r"\d[A-Z]{3}\d{3}", m["code"])]
print(f"\nNon-standard codes: {len(odd)}")
print(odd[:10])