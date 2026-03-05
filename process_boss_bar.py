from PIL import Image

input_path = "ChatGPT Image 28 feb 2026, 11_08_27 a.m..png"
output_path = "boss_bar.png"

# Load the image
img = Image.open(input_path).convert("RGBA")

# Extract non-white pixels
datas = img.getdata()
newData = []
for item in datas:
    # change all white (also shades of white)
    if item[0] > 240 and item[1] > 240 and item[2] > 240:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)

# Trim transparent edges to get the exact bar size
bbox = img.getbbox()
if bbox:
    img = img.crop(bbox)

img.save(output_path, "PNG")
print(f"Saved processed boss health bar to {output_path}")
