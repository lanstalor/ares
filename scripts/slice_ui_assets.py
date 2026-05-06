import argparse
import glob
import os
import shutil
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


INPUT_DIR = "assets/ui_assets_uploaded"
OUTPUT_DIR = "assets/ui_assets_wip"


def get_background_color(img):
    pixels = img[:, :, :3].reshape(-1, 3)
    quantized = (pixels // 10) * 10
    colors, counts = np.unique(quantized, axis=0, return_counts=True)
    dominant_quantized = colors[np.argmax(counts)]

    mask = np.all((pixels // 10) * 10 == dominant_quantized, axis=1)
    return np.median(pixels[mask], axis=0)


def build_foreground_mask(img, tolerance):
    bg_color = get_background_color(img)
    lower = np.clip(bg_color.astype(int) - tolerance, 0, 255).astype(np.uint8)
    upper = np.clip(bg_color.astype(int) + tolerance, 0, 255).astype(np.uint8)

    background_mask = np.all((img[:, :, :3] >= lower) & (img[:, :, :3] <= upper), axis=2)
    foreground_mask = ~background_mask

    # Clean isolated JPG/composite flecks before grouping nearby pixels.
    foreground_mask = ndimage.binary_opening(foreground_mask, structure=np.ones((2, 2), dtype=bool))
    return background_mask, foreground_mask, bg_color


def is_inside(inner, outer):
    x1, y1, w1, h1 = inner
    x2, y2, w2, h2 = outer
    return x1 >= x2 and y1 >= y2 and (x1 + w1) <= (x2 + w2) and (y1 + h1) <= (y2 + h2)


def crop_to_alpha(crop):
    alpha = crop[:, :, 3]
    ys, xs = np.nonzero(alpha)
    if len(xs) == 0 or len(ys) == 0:
        return None

    left, right = xs.min(), xs.max() + 1
    top, bottom = ys.min(), ys.max() + 1
    return crop[top:bottom, left:right]


def reject_reason(box, stats_area, foreground_mask, image_shape, pack_name):
    x, y, w, h = box
    img_h, img_w = image_shape[:2]
    img_area = img_h * img_w
    box_area = w * h
    fg_area = int(np.count_nonzero(foreground_mask[y : y + h, x : x + w]))
    density = fg_area / box_area if box_area else 0
    aspect = w / h if h else 999

    # The uploaded sheets have a marketing/header strip and instructional footer.
    if y < img_h * 0.055:
        return "catalog header"
    if pack_name != "asset_pack3" and y < img_h * 0.18 and (w > 35 or density < 0.5):
        return "catalog label"
    if y + h > img_h * 0.92:
        return "catalog footer"

    # Full-row separators and page/container outlines are sheet layout, not assets.
    if w > img_w * 0.86 or h > img_h * 0.86:
        return "sheet frame"
    if w > img_w * 0.38 and h > img_h * 0.32:
        return "category block"

    if w < 12 or h < 12:
        return "tiny speck"
    if fg_area < max(36, img_area * 0.00002):
        return "low foreground"

    # Text fragments on these sheets are usually short, sparse, and unframed.
    if h <= 22 and aspect >= 2.0 and density < 0.52:
        return "thin text"
    if h <= 36 and w >= 42 and density < 0.34:
        return "label text"
    if h <= 36 and w >= 86:
        return "section label"
    if h <= 48 and aspect >= 4.5 and density < 0.44:
        return "long label"
    if h <= 34 and 40 <= w <= 130 and density < 0.62:
        return "small text plate"

    # Catalog description blocks are often left-side multiline text.
    if x < img_w * 0.105 and h > 34:
        return "family copy"

    # Decorative scale bars and barcodes are useful only as part of a framed panel.
    if aspect >= 7.0 and h <= 38 and density < 0.46:
        return "wide rule"
    if 28 <= w <= 95 and 34 <= h <= 105 and density < 0.38:
        return "barcode or microtext"
    if h >= 42 and w <= 80 and density < 0.20:
        return "vertical label"

    # Very sparse connected components are usually anti-aliased text/noise.
    if density < 0.055 and stats_area < img_area * 0.004:
        return "sparse noise"

    return None


def collect_boxes(img, foreground_mask, close_kernel, pack_name):
    kernel = np.ones((close_kernel, close_kernel), dtype=bool)
    closed_mask = ndimage.binary_closing(foreground_mask, structure=kernel)
    labels, num_labels = ndimage.label(closed_mask, structure=np.ones((3, 3), dtype=bool))
    slices = ndimage.find_objects(labels)

    boxes = []
    rejected = {}
    for label_idx, component_slice in enumerate(slices, start=1):
        if component_slice is None:
            continue
        y_slice, x_slice = component_slice
        y = int(y_slice.start)
        x = int(x_slice.start)
        h = int(y_slice.stop - y_slice.start)
        w = int(x_slice.stop - x_slice.start)
        box = (x, y, w, h)
        stats_area = int(np.count_nonzero(labels[component_slice] == label_idx))
        reason = reject_reason(box, stats_area, foreground_mask, img.shape, pack_name)
        if reason:
            rejected[reason] = rejected.get(reason, 0) + 1
            continue
        boxes.append(box)

    final_boxes = []
    for box in boxes:
        if not any(box != other and is_inside(box, other) for other in boxes):
            final_boxes.append(box)

    final_boxes.sort(key=lambda item: (item[1], item[0]))
    return final_boxes, rejected


def process_image(filepath, output_dir, clean=False, tolerance=15, close_kernel=10):
    print(f"Reading {filepath}...")
    try:
        img = np.array(Image.open(filepath).convert("RGBA"))
    except OSError:
        print(f"Failed to read {filepath}")
        return 0

    background_mask, foreground_mask, bg_color = build_foreground_mask(img, tolerance)
    print(f"  Detected background color: {bg_color.astype(int).tolist()}")

    img[background_mask] = [0, 0, 0, 0]

    pack_name = Path(filepath).stem
    out_dir = Path(output_dir) / pack_name
    if clean and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    boxes, rejected = collect_boxes(img, foreground_mask, close_kernel, pack_name)

    written = 0
    for written, (x, y, w, h) in enumerate(boxes, start=1):
        cropped = crop_to_alpha(img[y : y + h, x : x + w])
        if cropped is None:
            continue
        out_path = out_dir / f"slice_{written:03d}.png"
        Image.fromarray(cropped, mode="RGBA").save(out_path)

    reason_text = ", ".join(f"{reason}: {count}" for reason, count in sorted(rejected.items()))
    print(f"  Saved {written} slices to {out_dir}")
    if reason_text:
        print(f"  Rejected {sum(rejected.values())}: {reason_text}")
    return written


def parse_args():
    parser = argparse.ArgumentParser(description="Slice uploaded UI asset sheets into transparent PNGs.")
    parser.add_argument("--input-dir", default=INPUT_DIR)
    parser.add_argument("--output-dir", default=OUTPUT_DIR)
    parser.add_argument("--packs", help="Comma-separated pack stems or filenames, e.g. asset_pack3,asset_pack9")
    parser.add_argument("--clean", action="store_true", help="Remove each pack output directory before writing.")
    parser.add_argument("--tolerance", type=int, default=15, help="Background color tolerance.")
    parser.add_argument("--close-kernel", type=int, default=10, help="Morphological close kernel size.")
    return parser.parse_args()


def main():
    args = parse_args()
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    images = sorted(glob.glob(os.path.join(args.input_dir, "*.png")))
    if args.packs:
        wanted = {Path(pack.strip()).stem for pack in args.packs.split(",") if pack.strip()}
        images = [path for path in images if Path(path).stem in wanted]

    total = 0
    for img_path in images:
        total += process_image(
            img_path,
            args.output_dir,
            clean=args.clean,
            tolerance=args.tolerance,
            close_kernel=args.close_kernel,
        )
    print(f"Done slicing {len(images)} sheet(s), {total} slice(s).")


if __name__ == "__main__":
    main()
