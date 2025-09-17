#!/usr/bin/env python3
"""
Download any images of a person,
then immediately run the cropper on the *newly downloaded* images.

Usage:
  python find_images.py <url1> <url2> ...
"""

import sys
import os
import time
import urllib.request
import urllib.error
from typing import List

# Import our cropper
import crop_images  # expects crop_images.py in the same directory

UA = "Mozilla/5.0 (compatible; ImageFetcher/1.0)"

ORIGINAL_DIR = "original"   # where we save the raw downloads
CROPPED_DIR = "cropped"     # where cropper writes circular PNGs

def head(url: str, timeout: float = 10.0) -> int:
    """Return HTTP status for HEAD; fall back to GET if needed."""
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        if e.code in (405, 501):
            return head_fallback_get(url, timeout)
        return e.code
    except urllib.error.URLError:
        return 0


def head_fallback_get(url: str, timeout: float = 10.0) -> int:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except urllib.error.URLError:
        return 0


def download(url: str, out_path: str, timeout: float = 30.0) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(out_path, "wb") as f:
        while True:
            chunk = resp.read(8192)
            if not chunk:
                break
            f.write(chunk)


def main(urls: List[str]) -> None:
    if not urls:
       raise ValueError("No URLs provided")

    os.makedirs(ORIGINAL_DIR, exist_ok=True)

    newly_downloaded: list[str] = []

    for url in urls:
        code = head(url)
        if code == 200:
            ok = True

        if not ok:
            print(f"[{url}] No public image found.")
            continue

        filename = url.split("/")[-1]

        if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
            pass
        else:
            print(f"[{url}] URL does not end with .jpg/.jpeg/.png, skipping.")
            continue

        out_path = os.path.join(ORIGINAL_DIR, filename)
        try:
            download(url, out_path)
            newly_downloaded.append(out_path)
            print(f"[{url}] Downloaded → {out_path}\n      URL: {url}\n")
        except Exception as e:
            print(f"[{url}] Found URL but failed to download: {url}\n  Error: {e}")

    # 🔧 Now crop only the newly downloaded images
    if newly_downloaded:
        print(f"[CROP] Processing {len(newly_downloaded)} new image(s)…")
        crop_images.crop_specific_files(newly_downloaded, output_root=CROPPED_DIR)
    else:
        print("[CROP] Nothing new to process.")


if __name__ == "__main__":
    main(sys.argv[1:])
