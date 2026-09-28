import os
import re

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
    html = f.read()

# Let's check IDs in index.html
ids = re.findall(r'id=["\']([^"\']+)["\']', html)
print("Existing IDs in index.html:", set(ids))

# Let's check data-path attributes
data_paths = re.findall(r'data-path=["\']([^"\']+)["\']', html)
print("Data paths in index.html:", set(data_paths))
