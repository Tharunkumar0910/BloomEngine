import os
from PIL import Image

src_img_path = r"C:\Users\pushp\.gemini\antigravity-ide\brain\309893ca-e33b-40d5-9a0b-642dfbe55858\media__1784800760711.png"
output_dir = r"c:\Tharun\BloomAI_Arena_v2_1\static\images\logo"

img = Image.open(src_img_path).convert("RGBA")

def make_white_transparent(image, threshold=240):
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

# 1. Full horizontal logo (Top main logo: x: 190..840, y: 70..200)
full_logo = img.crop((190, 70, 840, 200))
full_logo_trans = make_white_transparent(full_logo)
full_logo_trans.save(os.path.join(output_dir, "bloomengine-logo.png"), "PNG")

# 2. Icon only (x: 555..665, y: 340..440)
icon_logo = img.crop((555, 340, 665, 440))
icon_logo_trans = make_white_transparent(icon_logo)
icon_logo_trans.save(os.path.join(output_dir, "bloomengine-icon.png"), "PNG")

# 3. Square app icon (x: 770..910, y: 335..455)
app_logo = img.crop((770, 335, 910, 455))
app_logo.save(os.path.join(output_dir, "bloomengine-app-icon.png"), "PNG")

# 4. Favicon PNG (64x64) & Favicon ICO (32x32)
fav_png = icon_logo_trans.resize((64, 64), Image.Resampling.LANCZOS)
fav_png.save(os.path.join(output_dir, "favicon.png"), "PNG")

fav_ico = icon_logo_trans.resize((32, 32), Image.Resampling.LANCZOS)
fav_ico.save(os.path.join(output_dir, "favicon.ico"), format="ICO", sizes=[(32, 32)])

print("Extracted exact branding crops successfully!")
