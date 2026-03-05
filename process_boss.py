from PIL import Image
import os

def crop_boss(image_path, output_dir):
    try:
        img = Image.open(image_path).convert("RGBA")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Remove white background and make it transparent
        data = img.getdata()
        new_data = []
        for item in data:
            # If color is close to white, make transparent
            if item[0] > 230 and item[1] > 230 and item[2] > 230:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)
        
        # Define generous rough boxes around each sprite (x1, y1, x2, y2)
        # Top Left (Idle)
        box_idle = (40, 90, 320, 380)
        # Bottom Left (Angry)
        box_angry = (40, 500, 320, 800)
        # Center (Big Idle)
        box_big = (340, 180, 720, 580)
        # Top Right (Attack)
        box_attack = (700, 90, 980, 380)
        # Bottom Right (Damaged)
        box_damage = (700, 500, 980, 800)
        
        boxes = {
            "idle": box_idle,
            "angry": box_angry,
            "big": box_big,
            "attack": box_attack,
            "damage": box_damage
        }
        
        for name, box in boxes.items():
            cropped = img.crop(box)
            # Auto-trim the transparent borders for a perfect tight crop
            bbox = cropped.getbbox()
            if bbox:
                perfect_crop = cropped.crop(bbox)
                perfect_crop.save(os.path.join(output_dir, f"boss_{name}.png"))
                print(f"Saved boss_{name}.png with perfectly trimmed bounds.")
            else:
                print(f"Warning: Blank bounding box for {name}.")
        
        print("Boss sprites auto-cropped successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    crop_boss("boss_spritesheet.png", "boss_frames")
