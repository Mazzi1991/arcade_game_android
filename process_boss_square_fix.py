from PIL import Image, ImageDraw

def process_boss_floodfill(image_path, output_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        
        # We need a mask to find the contiguous background
        # ImageDraw.floodfill works on RGB/L, so let's make a copy
        mask = Image.new('L', img.size, 0)
        
        # We'll flood fill on a temporary white-background RGB version
        temp_img = Image.new("RGB", img.size, (255, 255, 255))
        temp_img.paste(img, (0, 0), img)
        
        # Flood fill from the four corners with a distinct color (e.g. magenta)
        target_color = (255, 0, 255)
        thresh = 40 # tolerance for "white"
        
        corners = [
            (0, 0),
            (img.width - 1, 0),
            (0, img.height - 1),
            (img.width - 1, img.height - 1)
        ]
        
        for corner in corners:
            # Check if corner is near white
            pixel = temp_img.getpixel(corner)
            if pixel[0] > 200 and pixel[1] > 200 and pixel[2] > 200:
                ImageDraw.floodfill(temp_img, corner, target_color, thresh=thresh)
                
        # Now apply the transparency where temp_img is magenta
        data = img.getdata()
        temp_data = temp_img.getdata()
        new_data = []
        for i in range(len(data)):
            if temp_data[i] == target_color:
                new_data.append((255, 255, 255, 0)) # transparent
            else:
                new_data.append(data[i]) # original pixel
                
        img.putdata(new_data)
        
        # Auto-trim the transparent borders for a perfect tight crop
        bbox = img.getbbox()
        if bbox:
            perfect_crop = img.crop(bbox)
            perfect_crop.save(output_path)
            print("Successfully processed and saved the square boss sprite with floodfill!")
        else:
            print("Warning: Blank bounding box for boss.")
            
    except Exception as e:
        print(f"Error processing boss: {e}")

if __name__ == "__main__":
    process_boss_floodfill("boss_square_raw.png", "boss_square.png")
