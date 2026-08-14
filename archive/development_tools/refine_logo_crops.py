import os
from PIL import Image

src_img_path = r"C:\Users\pushp\.gemini\antigravity-ide\brain\309893ca-e33b-40d5-9a0b-642dfbe55858\media__1784800760711.png"
output_dir = r"c:\Tharun\BloomAI_Arena_v2_1\static\images\logo"

img = Image.open(src_img_path).convert("RGBA")
w, h = img.size

# Helper to crop tight around non-white content within a subregion
def get_tight_crop(img, box, threshold=240):
    sub = img.crop(box)
    pixels = sub.load()
    sw, sh = sub.size
    min_x, min_y, max_x, max_y = sw, sh, 0, 0
    for y in range(sh):
        for x in range(sw):
            r, g, b, a = pixels[x, y]
            if a > 10 and not (r > threshold and g > threshold and b > threshold):
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y
    
    if min_x <= max_x and min_y <= max_y:
        pad = 4
        min_x = max(0, min_x - pad)
        min_y = max(0, min_y - pad)
        max_x = min(sw, max_x + pad)
        max_y = min(sh, max_y + pad)
        return sub.crop((min_x, min_y, max_x, max_y))
    return sub

# Helper to convert white background to transparent
def make_white_transparent(image, threshold=235):
    img_conv = image.convert("RGBA")
    datas = img_conv.getdata()
    new_data = []
    for item in datas:
        r, g, b, a = item
        if r >= threshold and g >= threshold and b >= threshold:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img_conv.putdata(new_data)
    return img_conv

# 1. Full horizontal logo (Top center)
logo_region = (int(w * 0.15), int(h * 0.05), int(w * 0.85), int(h * 0.32))
full_logo = get_tight_crop(img, logo_region)
full_logo_trans = make_white_transparent(full_logo)
full_logo_trans.save(os.path.join(output_dir, "bloomengine-logo.png"), "PNG")

# 2. Icon only (middle center below "ICON ONLY" label: y: 0.35..0.48, x: 0.54..0.66)
icon_region = (int(w * 0.54), int(h * 0.35), int(w * 0.66), int(h * 0.48))
icon_logo = get_tight_crop(img, icon_region)
icon_logo_trans = make_white_transparent(icon_logo)
icon_logo_trans.save(os.path.join(output_dir, "bloomengine-icon.png"), "PNG")

# 3. Square app icon (middle right below label: y: 0.34..0.48, x: 0.75..0.89)
app_region = (int(w * 0.75), int(h * 0.34), int(w * 0.89), int(h * 0.48))
app_logo = get_tight_crop(img, app_region)
app_logo.save(os.path.join(output_dir, "bloomengine-app-icon.png"), "PNG")

# 4. Favicon PNG (64x64) and Favicon ICO (32x32)
fav_png = icon_logo_trans.resize((64, 64), Image.Resampling.LANCZOS)
fav_png.save(os.path.join(output_dir, "favicon.png"), "PNG")

fav_ico = icon_logo_trans.resize((32, 32), Image.Resampling.LANCZOS)
fav_ico.save(os.path.join(output_dir, "favicon.ico"), format="ICO", sizes=[(32, 32)])

print("Successfully regenerated clean transparent assets in static/images/logo/")
