import re

with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

pattern = "def generate_dynamic_explanation"
for i, line in enumerate(lines):
    if pattern in line:
        print(f"Line {i+1}: {line.strip()}")
