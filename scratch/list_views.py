import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    content = f.read()

views = re.findall(r'id=["\'](view-[a-zA-Z0-9_-]+)["\']', content)
print("Found views:")
for v in views:
    print(f"- {v}")
