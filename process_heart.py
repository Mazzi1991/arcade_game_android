from PIL import Image
import os

input_path = "ChatGPT Image 28 feb 2026, 10_46_51 a.m..png"
output_path = "heart.png"

# Load the image
img = Image.open(input_path).convert("RGBA")

# Get bounding box of all non-white pixels
# We want to extract the first heart with the sparkles.
# First, let's just make the white background transparent.
datas = img.getdata()
newData = []
for item in datas:
    # change all white (also shades of white)
    if item[0] > 240 and item[1] > 240 and item[2] > 240:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)

# Let's crop to just the left-most heart
# Since it's 3 hearts, we can just take the left third approximately
width, height = img.size
cropped_img = img.crop((0, 0, width // 3, height))

# Let's trim the transparent edges from the cropped heart to get a clean bounding box
bbox = cropped_img.getbbox()
if bbox:
    cropped_img = cropped_img.crop(bbox)

cropped_img.save(output_path, "PNG")
print(f"Saved processed heart to {output_path}")
