#!/usr/bin/env python3
"""
Crop portraits into circular PNGs at multiple sizes.
- Detects largest face, crops a square around it with margin, then applies circular alpha.
- Exposes functions so other scripts (like the downloader) can call it.

Dependencies: pillow, opencv-python, numpy
pip install pillow opencv-python numpy
"""

import os
import cv2
import numpy as np
from PIL import Image
from typing import Iterable, List, Tuple

# Defaults (can be overridden by caller)
DIMENSIONS: List[int] = [256, 512, 1024]

# Preload the cascade
_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def _largest_face(gray: np.ndarray) -> Tuple[int, int, int, int] | None:
    faces = _face_cascade.detectMultiScale(gray, 1.1, 4)
    if len(faces) == 0:
        return None
    # x, y, w, h of the largest by area
    return max(faces, key=lambda r: r[2] * r[3])


def _square_crop_around(center: Tuple[int, int], radius: int, w: int, h: int) -> Tuple[int, int, int, int]:
    side = 2 * radius
    left = max(center[0] - radius, 0)
    top = max(center[1] - radius, 0)
    right = left + side
    bottom = top + side

    if right > w:
        right = w
        left = max(right - side, 0)
    if bottom > h:
        bottom = h
        top = max(bottom - side, 0)
    return left, top, right, bottom


def _to_square_center_crop(img: np.ndarray) -> np.ndarray:
    """Fallback: center-square crop if no face is found."""
    h, w = img.shape[:2]
    side = min(h, w)
    y0 = (h - side) // 2
    x0 = (w - side) // 2
    return img[y0:y0 + side, x0:x0 + side]


def _circle_mask(size: int) -> Image.Image:
    """Return a circular alpha mask (L mode) of given size."""
    mask = Image.new("L", (size, size), 0)
    # Use Pillow's draw for a crisp circle
    from PIL import ImageDraw
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, size - 1, size - 1), fill=255)
    return mask


def crop_and_save_one(input_path: str, output_root: str, dimensions: Iterable[int] = DIMENSIONS) -> list[str]:
    """
    Process a single image path and write circular PNGs under:
      {output_root}/{dim}/{basename}.png
    Returns list of output paths created.
    """
    os.makedirs(output_root, exist_ok=True)
    for d in dimensions:
        os.makedirs(os.path.join(output_root, str(d)), exist_ok=True)

    base = os.path.splitext(os.path.basename(input_path))[0]
    expected = [os.path.join(output_root, str(dim), f"{base}.png") for dim in dimensions]

    # Skip if all outputs already exist
    if all(os.path.exists(p) for p in expected):
        print(f"[SKIP] {base} → already cropped")
        return expected

    # Read with OpenCV (BGR)
    img = cv2.imread(input_path)
    if img is None:
        print(f"[WARN] Could not read image: {input_path}")
        return []

    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face = _largest_face(gray)

    if face is not None:
        x, y, fw, fh = face
        # margin ~ 120% of max face size
        margin = int(1.2 * max(fw, fh))
        radius = max(fw, fh) // 2 + margin // 2
        cx, cy = x + fw // 2, y + fh // 2
        left, top, right, bottom = _square_crop_around((cx, cy), radius, w, h)
        cropped = img[top:bottom, left:right]
    else:
        print(f"[INFO] No face found in {os.path.basename(input_path)} — using center square crop.")
        cropped = _to_square_center_crop(img)

    # Ensure square (protect against edge/bounds adjustments)
    ch, cw = cropped.shape[:2]
    if ch != cw:
        side = min(ch, cw)
        y0 = (ch - side) // 2
        x0 = (cw - side) // 2
        cropped = cropped[y0:y0 + side, x0:x0 + side]

    # Convert to RGB for Pillow
    pil_square = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))

    out_paths: list[str] = []
    base = os.path.splitext(os.path.basename(input_path))[0]

    for dim in dimensions:
        resized = pil_square.resize((dim, dim), Image.LANCZOS).convert("RGBA")
        alpha = _circle_mask(dim)
        resized.putalpha(alpha)

        out_path = os.path.join(output_root, str(dim), f"{base}.png")
        resized.save(out_path)
        out_paths.append(out_path)
        print(f"[OK] Cropped and saved: {out_path}")

    return out_paths


def crop_specific_files(files: Iterable[str], output_root: str = "cropped", dimensions: Iterable[int] = DIMENSIONS) -> None:
    for f in files:
        crop_and_save_one(f, output_root=output_root, dimensions=dimensions)


def crop_folder(input_folder: str = "original", output_root: str = "cropped", dimensions: Iterable[int] = DIMENSIONS) -> None:
    files = [
        os.path.join(input_folder, fn)
        for fn in os.listdir(input_folder)
        if fn.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    crop_specific_files(files, output_root, dimensions)


if __name__ == "__main__":
    # CLI: process everything in "original"
    crop_folder()
