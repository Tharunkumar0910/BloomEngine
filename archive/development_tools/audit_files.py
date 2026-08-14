import os
import sys

base_dir = r"c:\Tharun\BloomAI_Arena_v2_1"

files_to_check = [
    "templates/landing.html",
    "templates/auth.html",
    "static/css/landing.css",
    "static/css/auth.css",
    "static/js/landing.js",
    "static/js/auth.js",
]

print("=== FILE EXISTENCE AUDIT ===")
for rel_path in files_to_check:
    full_path = os.path.join(base_dir, rel_path)
    exists = os.path.isfile(full_path)
    size = os.path.getsize(full_path) if exists else 0
    print(f"[{'EXISTS' if exists else 'MISSING'}] {rel_path} ({size} bytes)")
