import glob

for path in glob.glob(r"c:\Tharun\BloomAI_Arena_v2_1\templates\*.html"):
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if "BloomStudio" in line or "bolt" in line:
                print(f"{path} Line {i}: {line.strip()[:100]}")
