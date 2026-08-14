with open(r"c:\Tharun\BloomAI_Arena_v2_1\templates\index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if "Studio" in line or "bolt" in line or "Engine" in line or "brand" in line.lower() or "title" in line.lower():
        if i <= 150:
            print(f"Line {i}: {line.strip()}")
