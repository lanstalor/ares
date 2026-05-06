import cv2
import numpy as np

def test_bg_color(file):
    img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
    pixels = img[:,:,:3].reshape(-1, 3)
    quantized = (pixels // 10) * 10
    colors, counts = np.unique(quantized, axis=0, return_counts=True)
    dominant_quantized = colors[np.argmax(counts)]
    
    mask = np.all((pixels // 10) * 10 == dominant_quantized, axis=1)
    median_color = np.median(pixels[mask], axis=0)
    print(f"{file} -> Dominant Quantized: {dominant_quantized}, Median True Color: {median_color}")

for file in ["assets/ui_assets_uploaded/asset_pack6.png", "assets/ui_assets_uploaded/asset_pack4.png"]:
    test_bg_color(file)
