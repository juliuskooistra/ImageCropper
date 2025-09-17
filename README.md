# ImageCropper: Download and Crop Portrait Images

This toolset helps you download portrait images (from arbitrary URLs or specifically from the Berner Fachhochschule (BFH) website) and crop them into circular PNGs focused on faces, at multiple resolutions. It is designed for easy batch processing and high-quality results, especially for BFH staff images.

## Features

- **Download images from URLs** (arbitrary or BFH-specific)
- **Automatically detect and crop the largest face** in each image
- **Output circular PNGs** with transparent backgrounds at multiple sizes (default: 256, 512, 1024 px)
- **BFH-specific mode**: Tries multiple internal DAM/AEM URL patterns to fetch the highest quality available staff photo
- **Command-line and scriptable**: Use as CLI or import functions in your own scripts

## Requirements

- Python 3.8+
- [pillow](https://pypi.org/project/Pillow/)
- [opencv-python](https://pypi.org/project/opencv-python/)
- [numpy](https://pypi.org/project/numpy/)

Install dependencies:

```sh
pip install pillow opencv-python numpy
```

## Usage

### 1. Download and Crop from Arbitrary URLs

Use `find_images.py` to download images from any list of URLs, then crop them:

```sh
python find_images.py <url1> <url2> ...
```

Downloaded images are saved in the `original/` folder. Cropped, circular PNGs are saved in `cropped/<size>/`.

### 2. Download and Crop BFH Staff Images

Use `find_images_bfh.py` to fetch staff images by their BFH "Kurzel" (short ID, e.g. `rej6`, `gil4`). The script tries several internal URL patterns to find the highest quality image available, then downloads and crops it.

```sh
python find_images_bfh.py rej6 gil4 ...
# If no arguments are given, a default list of Kurzels is used.
```

### 3. Crop All Images in a Folder

You can also crop all images in the `original/` folder (e.g., after manual download):

```sh
python crop_images.py
```

### 4. Use as a Python Module

You can import and use the cropping functions in your own scripts:

```python
import crop_images
crop_images.crop_and_save_one('original/ktj1.jpg', 'cropped')
```

## Output Structure

- `original/` — Raw downloaded images (JPG/PNG)
- `cropped/256/`, `cropped/512/`, `cropped/1024/` — Circular PNGs at each size

## How It Works

1. **Download**: Images are fetched using Python's `urllib` (with a custom User-Agent).
2. **Face Detection**: The largest face is detected using OpenCV's Haar cascade. If no face is found, a center square crop is used.
3. **Cropping & Masking**: A square region around the face is cropped, resized, and a circular alpha mask is applied for a clean, round portrait.
4. **Saving**: PNGs are saved in the appropriate `cropped/<size>/` folders.

## BFH-Specific Download Logic

For BFH staff, the tool tries several internal URL patterns (AEM/DAM) to find the best available image quality. This often allows you to retrieve higher-resolution images than are publicly linked on the website.

## Example: Download and Crop for BFH Staff

```sh
python find_images_bfh.py heb1 rej6
# → Downloads and crops images for 'heb1' and 'rej6' if available
```

## Troubleshooting

- If an image cannot be downloaded or no face is detected, the script will print a warning and use a fallback crop.
- Make sure dependencies are installed and you have internet access for downloads.

## License

MIT License. See source files for details.
