import cv2
import numpy as np

def get_background_color(img):
    pixels = img[:,:,:3].reshape(-1, 3)
    quantized = (pixels // 10) * 10
    colors, counts = np.unique(quantized, axis=0, return_counts=True)
    dominant_quantized = colors[np.argmax(counts)]
    
    mask = np.all((pixels // 10) * 10 == dominant_quantized, axis=1)
    median_color = np.median(pixels[mask], axis=0)
    return median_color

def analyze_boxes(filepath):
    img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
    elif img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    bg_color = get_background_color(img)
    tolerance = 15
    lower = np.clip(bg_color.astype(int) - tolerance, 0, 255).astype(np.uint8)
    upper = np.clip(bg_color.astype(int) + tolerance, 0, 255).astype(np.uint8)
    
    mask = cv2.inRange(img[:,:,:3], lower, upper)
    fg_mask = cv2.bitwise_not(mask)
    
    # 1. Mild morphological close to group text inside panels, but not so much it merges adjacent panels
    kernel = np.ones((8, 8), np.uint8)
    closed_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed_mask, connectivity=8)
    
    img_h, img_w = img.shape[:2]
    
    boxes = []
    for i in range(1, num_labels):
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        
        if w < 10 or h < 10:
            continue
            
        # Let's print the dimensions of large boxes
        if w > img_w * 0.2 or h > img_h * 0.2:
            print(f"Large box found: w={w} ({w/img_w:.2f}), h={h} ({h/img_h:.2f})")
            
        boxes.append((x, y, w, h))
        
    print(f"Total raw boxes: {len(boxes)}")

analyze_boxes("assets/ui_assets_uploaded/asset_pack15.png")
