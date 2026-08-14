import glob

for path in glob.glob(r"c:\Tharun\BloomAI_Arena_v2_1\**\*.js", recursive=True) + glob.glob(r"c:\Tharun\BloomAI_Arena_v2_1\**\*.html", recursive=True):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f, 1):
            if "btnClassify" in line or "manualQuestion" in line or "btnClear" in line:
                print(f"{path} Line {i}: {line.strip()[:100]}")
