with open(r"c:\Tharun\BloomAI_Arena_v2_1\static\js\main.js", "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f, 1):
        if "Chart" in line or "chart" in line or "doughnut" in line.lower() or "legend" in line.lower():
            if "function" in line or "var " in line or "let " in line or "const " in line or "id" in line:
                print(f"Line {i}: {line.strip()[:100]}")
