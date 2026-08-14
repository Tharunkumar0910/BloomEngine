import re

def check_file(filepath):
    print(f"Checking {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if 'location' in line or 'href' in line or 'redirect' in line:
                print(f"Line {i}: {line.strip()[:120]}")

check_file(r"c:\Tharun\BloomAI_Arena_v2_1\templates\index.html")
check_file(r"c:\Tharun\BloomAI_Arena_v2_1\static\js\main.js")
