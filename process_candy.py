from PIL import Image
import os

def process_candy(image_path, output_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        
        # Remove white/light background and make it transparent
        data = img.getdata()
        new_data = []
        for item in data:
            # If color is close to white, make transparent
            if item[0] > 230 and item[1] > 230 and item[2] > 230:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)
        
        # Auto-trim the transparent borders for a perfect tight crop
        bbox = img.getbbox()
        if bbox:
            perfect_crop = img.crop(bbox)
            perfect_crop.save(output_path)
            print("Successfully processed and saved the candy sprite!")
        else:
            print("Warning: Blank bounding box for candy.")
            
    except Exception as e:
        print(f"Error processing candy: {e}")

if __name__ == "__main__":
    process_candy("candy_raw.png", "candy.png")
