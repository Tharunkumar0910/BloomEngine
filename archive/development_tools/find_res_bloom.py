with open(r"c:\Tharun\BloomAI_Arena_v2_1\static\js\main.js", "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f, 1):
        if "resBloom" in line or "resDiff" in line or "resExplanation" in line:
            print(f"Line {i}: {line.strip()[:100]}")
