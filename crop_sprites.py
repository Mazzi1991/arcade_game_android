from PIL import Image
import os

def crop_sprites(image_path, output_dir):
    try:
        img = Image.open(image_path)
        img = img.convert("RGBA")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Coordinates loosely based on visual inspection of the provided 1024x768 image
        # Let's extract the bottom row of small poodles for a walking animation Left to Right
        # And the middle left one, and top left one
        
        # Middle left (standing right)
        box_stand_right = (40, 360, 275, 620)
        img.crop(box_stand_right).save(os.path.join(output_dir, "player_stand_right.png"))
        
        # Middle right (standing left)
        box_stand_left = (720, 360, 955, 630)
        img.crop(box_stand_left).save(os.path.join(output_dir, "player_stand_left.png"))
        
        print("Sprites cropped successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    crop_sprites("player_spritesheet.png", "player_frames")
