import re

with open("index.html", "r", encoding="utf-8") as f:
    text = f.read()

panels = re.findall(r'id=["\']p-([a-zA-Z0-9_\-]+)["\']', text)
print("Panels:", panels)

charts = re.findall(r'new Chart\s*\(\s*([^,\n]+)', text)
print("Charts initialized:", len(charts))
for c in charts:
    print(" -", c.strip())
