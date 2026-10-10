import re
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET

# Use the newest run folder that has the full set of module files
runs = sorted(Path("data/raw/events").glob("*"), key=lambda p: len(list(p.glob("m*.xml"))))
run = runs[-1]
print("Checking folder:", run.name, "| files:", len(list(run.glob("m*.xml"))))

pat = re.compile(r"(\d{4})/(\d{2})/(\d{2})")
implied, spans, no_span = Counter(), Counter(), []

for f in run.glob("m*.xml"):
    root = ET.parse(f).getroot()
    found = False
    for span in root.iter("span"):
        desc = span.findtext("description") or ""
        dates = pat.findall(desc)
        if not dates:
            continue
        found = True
        first = date(*map(int, dates[0]))
        rawix = int(span.get("rawix", "1"))
        implied[first - timedelta(weeks=rawix - 1)] += 1
        spans[desc] += 1
    if not found:
        no_span.append(f.name)

print("Files without a dated span:", len(no_span), no_span[:5])
print("Implied week-1 dates:")
for d, n in implied.most_common():
    print(f"  {d} ({d:%A}): {n} spans")
print("Top span descriptions:")
for t, n in spans.most_common(5):
    print(f"  {n:4} {t}")