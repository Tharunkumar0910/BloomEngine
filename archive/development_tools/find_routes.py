import re

with open(r"c:\Tharun\BloomAI_Arena_v2_1\app.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if "@app.route" in line:
            print(f"Line {i}: {line.strip()}")
