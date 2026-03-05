import os
import glob

# Find the file with "07_42" in the name
files = glob.glob("*07_42*.png")
for f in files:
    print(f"Found: {f}")
    os.rename(f, "new_player.png")
    print("Renamed to new_player.png")
