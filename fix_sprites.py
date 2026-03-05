from PIL import Image
import os

def process_sprite(image_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        
        # Center dog is roughly in the middle
        # Let's crop a generous box around the center
        width, height = img.size
        # Center dog:
        box = (300, 80, 700, 480) 
        
        cropped = img.crop(box)
        
        # Remove white background
        data = cropped.getdata()
        new_data = []
        for item in data:
            # item is (R, G, B, A)
            # If it's very close to white, make it transparent
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
                
        cropped.putdata(new_data)
        
        # Trim transparent borders to get the exact bounding box
        bbox = cropped.getbbox()
        if bbox:
            cropped = cropped.crop(bbox)
            
        if not os.path.exists("player_frames"):
            os.makedirs("player_frames")
            
        # This dog is facing right
        cropped.save("player_frames/player_stand_right.png")
        
        # Flip for left facing
        flipped = cropped.transpose(Image.FLIP_LEFT_RIGHT)
        flipped.save("player_frames/player_stand_left.png")
        
        print("Fixed sprites successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_sprite("player_spritesheet.png")
