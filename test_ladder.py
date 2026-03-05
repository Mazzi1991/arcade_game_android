from PIL import Image

img = Image.open('ladder.png')
print("Active Ladder Size:", img.size)
print("Any fully transparent borders?")
bbox = img.getbbox()
print("Actual Non-Transparent BBox:", bbox)
