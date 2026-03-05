import os
import glob

files = glob.glob("*07_52*.png")
for f in files:
    print(f"Found: {f}")
    os.rename(f, "boss_spritesheet.png")
    print("Renamed to boss_spritesheet.png")
