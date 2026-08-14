import os
import glob
import time

search_dirs = [
    r"C:\Users\pushp\.gemini\antigravity-ide",
    r"C:\Users\pushp\AppData\Local\Temp",
    r"c:\Tharun\BloomAI_Arena_v2_1"
]

print("=== SEARCHING FOR ATTACHED BRANDING IMAGE ===")
found_images = []
for sdir in search_dirs:
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
        for path in glob.glob(os.path.join(sdir, '**', ext), recursive=True):
            mtime = os.path.getmtime(path)
            # Find images created in the last 1 hour
            if time.time() - mtime < 3600:
                found_images.append((mtime, path))

found_images.sort(reverse=True)
for mtime, path in found_images[:10]:
    print(f"{time.ctime(mtime)}: {path}")
