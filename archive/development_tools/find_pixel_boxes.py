from PIL import Image

img = Image.open(r"C:\Users\pushp\.gemini\antigravity-ide\brain\309893ca-e33b-40d5-9a0b-642dfbe55858\media__1784800760711.png").convert("RGB")
w, h = img.size
print(f"Image dimensions: {w}x{h}")

pixels = img.load()
purple_coords = []
for y in range(h):
    for x in range(w):
        r, g, b = pixels[x, y]
        # Check for purple #6D4AFF approx (109, 74, 255) or (120, 80, 240)
        if b > 200 and r < 150 and g < 120:
            purple_coords.append((x, y))

print(f"Found {len(purple_coords)} purple pixels.")

# Group purple pixels by x regions:
# Left logo icon: x around 0..400
# Center icon only: x around 450..700
# Right app icon: x around 700..1024

center_pixels = [p for p in purple_coords if 450 <= p[0] <= 700]
if center_pixels:
    xs = [p[0] for p in center_pixels]
    ys = [p[1] for p in center_pixels]
    print(f"Center Icon Only box: x=({min(xs)}, {max(xs)}), y=({min(ys)}, {max(ys)})")

right_pixels = [p for p in purple_coords if 700 <= p[0] <= 1000]
if right_pixels:
    xs = [p[0] for p in right_pixels]
    ys = [p[1] for p in right_pixels]
    print(f"Right App Icon box: x=({min(xs)}, {max(xs)}), y=({min(ys)}, {max(ys)})")

full_logo_pixels = [p for p in purple_coords if p[0] < 450]
if full_logo_pixels:
    xs = [p[0] for p in full_logo_pixels]
    ys = [p[1] for p in full_logo_pixels]
    print(f"Full Logo box: x=({min(xs)}, {max(xs)}), y=({min(ys)}, {max(ys)})")
