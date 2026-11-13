import re

with open("index.html", "r", encoding="utf-8") as f:
    text = f.read()

calls = re.findall(r'createChart\s*\(\s*["\']([^"\']+)["\']', text)
print("createChart calls:", calls)

canvases = re.findall(r'<canvas\s+[^>]*id=["\']([^"\']+)["\']', text)
print("All HTML canvases:", canvases)
