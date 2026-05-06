import os
import json
import cv2
import numpy as np
import google.generativeai as genai
from pathlib import Path

# Setup
API_KEY = "AIzaSyBQ3zSI0u876OsBtCkoEk3Tgy5Q8pLV8Bc"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-flash-latest")

INPUT_DIR = Path("assets/ui_assets_wip")
OUTPUT_DIR = Path("assets/ui_assets_final")
REGISTRY_FILE = Path("assets/ui_registry.json")

def get_asset_name(image_path, pack_image_path):
    prompt = """
    Analyze this UI sprite. This sprite comes from the attached sprite sheet reference. 
    Look at the reference to see what this sprite is (e.g., look for nearby labels or the sprite's position).
    Return a JSON object with:
    {
      "name": "snake_case_descriptive_name",
      "type": "button|panel|icon|divider|bar",
      "state": "default|hover|pressed|disabled",
      "category": "core|transition|overlay"
    }
    Just return the JSON.
    """
    
    img = genai.upload_file(image_path)
    ref_img = genai.upload_file(pack_image_path)
    response = model.generate_content([prompt, img, ref_img])
    json_text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(json_text)

def get_color_scheme(image_path):
    img = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
    if img is None: return "unknown"
    # Get only non-transparent pixels
    if img.shape[2] == 4:
        mask = img[:,:,3] > 128
        pixels = img[mask][:,:3]
    else:
        pixels = img.reshape(-1, 3)
    
    # Detect colors
    has_red = np.any(pixels[:, 2] > 150)
    has_orange = np.any(pixels[:, 2] > 150) and np.any(pixels[:, 1] > 100)
    has_cyan = np.any(pixels[:, 0] > 150) and np.any(pixels[:, 1] > 150)
    
    colors = ["grey"]
    if has_cyan: colors.append("cyan")
    elif has_orange: colors.append("orange")
    elif has_red: colors.append("red")
    
    return "_and_".join(colors)

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    registry = []
    
    for folder in INPUT_DIR.iterdir():
        if folder.is_dir():
            pack_image_path = Path("assets/ui_assets_uploaded") / f"{folder.name}.png"
            if not pack_image_path.exists(): continue
                
            for img_path in folder.glob("*.png"):
                try:
                    data = get_asset_name(str(img_path), str(pack_image_path))
                    
                    # Add metadata
                    img = cv2.imread(str(img_path), cv2.IMREAD_UNCHANGED)
                    if img is None: continue
                    h, w = img.shape[:2]
                    data['dimensions'] = {"w": w, "h": h}
                    data['color_scheme'] = get_color_scheme(img_path)
                    
                    new_filename = f"{data['category']}_{data['type']}_{data['name']}_{data['state']}.png"
                    new_path = OUTPUT_DIR / new_filename
                    
                    os.rename(img_path, new_path)
                    data['path'] = str(new_path)
                    registry.append(data)
                    print(f"Successfully processed {new_filename}")
                except Exception as e:
                    print(f"Error processing {img_path.name}: {e}")

    with open(REGISTRY_FILE, 'w') as f:
        json.dump(registry, f, indent=2)

if __name__ == "__main__":
    main()
