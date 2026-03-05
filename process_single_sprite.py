from PIL import Image
import os

def process_single_sprite(image_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        
        # Remove white background
        data = img.getdata()
        new_data = []
        for item in data:
            # item is (R, G, B, A)
            # If it's very close to white, make it transparent
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
                
        img.putdata(new_data)
        
        # Trim transparent borders to get the exact bounding box
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
            
        if not os.path.exists("player_frames"):
            os.makedirs("player_frames")
            
        # The provided new dog is facing right
        img.save("player_frames/player_stand_right.png")
        
        # Flip for left facing
        flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
        flipped.save("player_frames/player_stand_left.png")
        
        print("Processed single sprite successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_single_sprite("Gemini_Generated_Image_etmv2netmv2netmv.png")
