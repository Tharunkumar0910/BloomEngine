import os
from PIL import Image

src_img_path = r"C:\Users\pushp\.gemini\antigravity-ide\brain\309893ca-e33b-40d5-9a0b-642dfbe55858\media__1784800760711.png"
output_dir = r"c:\Tharun\BloomAI_Arena_v2_1\static\images\logo"

os.makedirs(output_dir, exist_ok=True)

img = Image.open(src_img_path)
print(f"Source Image Size: {img.size}, Mode: {img.mode}")

# Bounding boxes relative to source image dimensions (W, H):
# Source is approx 1000x650
w, h = img.size

# 1. Full horizontal logo (Top center / Left center)
# The full logo is in top center or left box: x: 180..820, y: 60..200
logo_crop = img.crop((int(w * 0.18), int(h * 0.08), int(w * 0.82), int(h * 0.32)))
logo_crop.save(os.path.join(output_dir, "bloomengine-logo.png"), "PNG")

# 2. Icon only (middle center x: 520..660, y: 480..630)
icon_crop = img.crop((int(w * 0.53), int(h * 0.48), int(w * 0.65), int(h * 0.67)))
icon_crop.save(os.path.join(output_dir, "bloomengine-icon.png"), "PNG")

# 3. Square app icon (middle right x: 740..900, y: 470..680)
app_icon_crop = img.crop((int(w * 0.74), int(h * 0.47), int(w * 0.90), int(h * 0.68)))
app_icon_crop.save(os.path.join(output_dir, "bloomengine-app-icon.png"), "PNG")

# 4. Favicon PNG & ICO
favicon_img = icon_crop.resize((64, 64), Image.Resampling.LANCZOS)
favicon_img.save(os.path.join(output_dir, "favicon.png"), "PNG")

favicon_ico = icon_crop.resize((32, 32), Image.Resampling.LANCZOS)
favicon_ico.save(os.path.join(output_dir, "favicon.ico"), format="ICO", sizes=[(32, 32)])

print("Extracted all branding assets successfully to static/images/logo/")
