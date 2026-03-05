from PIL import Image
import os

def process_ladder(image_path, output_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        
        # Remove white/light background and make it transparent
        data = img.getdata()
        new_data = []
        for item in data:
            # If color is close to white/light beige, make transparent
            if item[0] > 220 and item[1] > 220 and item[2] > 220:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)
        
        # Define a bounding box around the left ladder
        # Rough estimate based on image proportions
        width, height = img.size
        # The new image has ladders on left/right half.
        box = (0, 0, width // 2, height)
        
        cropped = img.crop(box)
        bbox = cropped.getbbox()
        if bbox:
            perfect_crop = cropped.crop(bbox)
            perfect_crop.save(output_path)
            print("Successfully processed and saved the ladder sprite!")
        else:
            print("Warning: Blank bounding box for ladder.")
            
    except Exception as e:
        print(f"Error processing ladder: {e}")

if __name__ == "__main__":
    process_ladder("ladder_raw.png", "ladder.png")
