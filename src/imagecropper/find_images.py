#!/usr/bin/env python3
"""
Download any images of a person, then immediately run the cropper
on the *newly downloaded* images.

Usage:
  imagecropper-fetch <url1> <url2> ...
  python -m imagecropper.find_images <url1> <url2> ...
"""

import argparse
import os
import urllib.request
import urllib.error
from typing import List

from . import crop_images

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


def main(urls: List[str], original_dir: str = ORIGINAL_DIR, cropped_dir: str = CROPPED_DIR) -> None:
    if not urls:
        raise ValueError("No URLs provided")

    os.makedirs(original_dir, exist_ok=True)

    newly_downloaded: list[str] = []

    for url in urls:
        if head(url) != 200:
            print(f"[{url}] No public image found.")
            continue

        filename = url.split("/")[-1]

        if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            print(f"[{url}] URL does not end with .jpg/.jpeg/.png/.webp, skipping.")
            continue

        out_path = os.path.join(original_dir, filename)
        try:
            download(url, out_path)
            newly_downloaded.append(out_path)
            print(f"[{url}] Downloaded → {out_path}\n      URL: {url}\n")
        except Exception as e:
            print(f"[{url}] Found URL but failed to download: {url}\n  Error: {e}")

    # 🔧 Now crop only the newly downloaded images
    if newly_downloaded:
        print(f"[CROP] Processing {len(newly_downloaded)} new image(s)…")
        crop_images.crop_specific_files(newly_downloaded, output_root=cropped_dir)
    else:
        print("[CROP] Nothing new to process.")


def cli(argv: list[str] | None = None) -> None:
    """Console-script entry point."""
    parser = argparse.ArgumentParser(
        prog="imagecropper-fetch",
        description="Download images from URLs, then crop the new ones.",
    )
    parser.add_argument("urls", nargs="+", metavar="URL", help="image URL(s) to download")
    parser.add_argument(
        "-o", "--output", default=CROPPED_DIR, metavar="DIR",
        help="folder to write cropped PNGs into (default: ./cropped)",
    )
    parser.add_argument(
        "--original", default=ORIGINAL_DIR, metavar="DIR",
        help="folder to save raw downloads into (default: ./original)",
    )
    args = parser.parse_args(argv)
    main(args.urls, original_dir=args.original, cropped_dir=args.output)


if __name__ == "__main__":
    cli()
