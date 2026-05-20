#!/usr/bin/env python3
"""
Download BFH person images by trying common AEM/DAM patterns,
then immediately run the cropper on the *newly downloaded* images.

Usage:
  python find_images_bfh.py rej6 gil4 ...
  # If no args given, it defaults to ["rej6", "gil4"].
"""

import sys
import os
import time
from typing import List

# Import our cropper
import crop_images  # expects crop_images.py in the same directory
# Import our downloader
import find_images # expects find_images.py in the same directory

BASE = "https://www.bfh.ch"
THEME = "bfh-theme"
UA = "Mozilla/5.0 (compatible; ImageFetcher/1.0)"

VARIANTS = [
    "profile-xl",
    "profile-lg",
    "teaser-xl",
    "teaser-lg",
    "og-image-sharing",
]

ORIGINAL_DIR = "original"   # where we save the raw downloads
CROPPED_DIR = "cropped"     # where cropper writes circular PNGs

KURZELS = [
    "heb1",
    "rej6",
    "gil4",
    "ktj1",
    "dsr2",
    "zex1",
    "kem2",
    "kem3",
    "kia2"
]

def candidates(img_id: str) -> List[str]:
    folder = img_id[0]  # first letter of the Kurzel
    imaging = [
        f"{BASE}/.imaging/mte/{THEME}/{variant}/dam/people/{folder}/{img_id}.jpg/jcr:content/{img_id}.jpg"
        for variant in VARIANTS
    ]
    dam = [
        f"{BASE}/dam/people/{folder}/{img_id}.jpg",
        f"{BASE}/dam/people/{folder}/{img_id}.jpg/_jcr_content/renditions/original",
        f"{BASE}/dam/people/{folder}/{img_id}/_jcr_content/renditions/original",
    ]
    return dam + imaging


def find_first_working_url(urls: List[str]) -> str | None:
    for u in urls:
        code = find_images.head(u)
        if code == 200:
            return u
        time.sleep(0.1)
    return None


def main(ids: List[str]) -> None:
    if not ids:
        ids = KURZELS

    os.makedirs(ORIGINAL_DIR, exist_ok=True)

    newly_downloaded: list[str] = []

    for img_id in ids:
        urls = candidates(img_id)
        ok = find_first_working_url(urls)

        if not ok:
            print(f"[{img_id}] No public image found.")
            continue

        out_path = os.path.join(ORIGINAL_DIR, f"{img_id}.jpg")
        try:
            find_images.download(ok, out_path)
            newly_downloaded.append(out_path)
            print(f"[{img_id}] Downloaded → {out_path}\n      URL: {ok}\n")
        except Exception as e:
            print(f"[{img_id}] Found URL but failed to download: {ok}\n  Error: {e}")

    # 🔧 Now crop only the newly downloaded images
    if newly_downloaded:
        print(f"[CROP] Processing {len(newly_downloaded)} new image(s)…")
        crop_images.crop_specific_files(newly_downloaded, output_root=CROPPED_DIR)
    else:
        print("[CROP] Nothing new to process.")


if __name__ == "__main__":
    main(sys.argv[1:])
