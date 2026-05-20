# ImageCropper: Download and Crop Portrait Images

This toolset helps you download portrait images (from arbitrary URLs or specifically from the Berner Fachhochschule (BFH) website) and crop them into circular and square PNGs focused on faces, at multiple resolutions. It is designed for easy batch processing and high-quality results, especially for BFH staff images.

It is packaged as a pip-installable Python package (`imagecropper`) — use it as a library in other projects or via its command-line tools.

## Features

- **Download images from URLs** (arbitrary or BFH-specific)
- **Automatically detect and crop the largest face** in each image
- **Output circular & square PNGs** with transparent backgrounds at multiple sizes (default: 256, 512, 1024 px)
- **BFH-specific mode**: Tries multiple internal DAM/AEM URL patterns to fetch the highest quality available staff photo
- **Command-line and scriptable**: Use the installed CLI tools or import functions in your own scripts

## Requirements

- Python 3.10+
- [pillow](https://pypi.org/project/Pillow/), [opencv-python](https://pypi.org/project/opencv-python/), [numpy](https://pypi.org/project/numpy/) — installed automatically with the package

## Installation

### Use it in another repository

Add it as a Git dependency. With pip:

```sh
pip install "git+ssh://git@github.com/juliuskooistra/ImageCropper.git"
```

Or pin a specific tag/commit for reproducible builds:

```sh
pip install "git+ssh://git@github.com/juliuskooistra/ImageCropper.git@v0.1.0"
```

In a `requirements.txt`:

```text
imagecropper @ git+ssh://git@github.com/juliuskooistra/ImageCropper.git@v0.1.0
```

In a `pyproject.toml` (PEP 508):

```toml
dependencies = [
    "imagecropper @ git+ssh://git@github.com/juliuskooistra/ImageCropper.git@v0.1.0",
]
```

> Use the `https://github.com/...` form instead of `ssh://git@github.com/...` if the repository is public or you authenticate over HTTPS.

### Develop on this repo locally

```sh
pip install -e .
```

This installs the package in editable mode and registers the CLI commands below.

## Usage

### As a Python library

```python
from imagecropper import crop_and_save_one, crop_folder, download

# Crop a single image into circle + square PNGs at every default size
crop_and_save_one("photo.jpg", output_root="cropped")

# Crop every image in a folder
crop_folder(input_folder="original", output_root="cropped")

# Crop only specific shapes/sizes
crop_and_save_one("photo.jpg", "cropped", shapes=["circle"], dimensions=[512])

# Download an image
download("https://example.com/portrait.jpg", "original/portrait.jpg")
```

### Command-line tools

After installing, three commands are available. By default they read/write `original/` and `cropped/` relative to your current directory; use the flags to point them elsewhere (absolute or relative paths both work).

```sh
# Download from arbitrary URLs, then crop the new images
imagecropper-fetch <url1> <url2> ... [-o DIR] [--original DIR]

# Download BFH staff images by Kurzel (short ID), then crop them
imagecropper-fetch-bfh rej6 gil4 ... [-o DIR] [--original DIR]
# If no Kurzels are given, a default list is used.

# Crop every image in an input folder
imagecropper-crop [-i DIR] [-o DIR]
```

Flags:

- `-o`, `--output DIR` — where cropped PNGs are written (default: `./cropped`)
- `--original DIR` — where raw downloads are saved, for the `fetch` commands (default: `./original`)
- `-i`, `--input DIR` — folder of source images for `imagecropper-crop` (default: `./original`)

Example — write results to a fixed location no matter where the command is run from:

```sh
imagecropper-fetch-bfh ktj1 rej6 -o /Users/you/project/assets/avatars
```

Run any command with `--help` for full usage. You can also run a module directly with `python -m`, e.g. `python -m imagecropper.crop_images -o build/avatars`.

## Public API

| Function | Description |
| --- | --- |
| `crop_and_save_one(input_path, output_root, shapes=..., dimensions=...)` | Crop one image; returns the list of output paths. |
| `crop_specific_files(files, output_root="cropped", ...)` | Crop a list of image paths. |
| `crop_folder(input_folder="original", output_root="cropped", ...)` | Crop every image in a folder. |
| `download(url, out_path, timeout=30.0)` | Download a single file. |
| `DIMENSIONS`, `SHAPES` | Default sizes (`[256, 512, 1024]`) and shapes (`["circle", "square"]`). |

## Output Structure

Cropped PNGs are written under `{output_root}/{shape}/{size}/{name}.png`, e.g.:

- `cropped/circle/256/`, `cropped/circle/512/`, `cropped/circle/1024/`
- `cropped/square/256/`, `cropped/square/512/`, `cropped/square/1024/`

## How It Works

1. **Download**: Images are fetched using Python's `urllib` (with a custom User-Agent).
2. **Face Detection**: The largest face is detected using OpenCV's Haar cascade. If no face is found, a center square crop is used.
3. **Cropping & Masking**: A square region around the face is cropped, resized, and a circular alpha mask is applied for a clean, round portrait.
4. **Saving**: PNGs are saved in the appropriate `cropped/<shape>/<size>/` folders.

## BFH-Specific Download Logic

For BFH staff, the tool tries several internal URL patterns (AEM/DAM) to find the best available image quality. This often allows you to retrieve higher-resolution images than are publicly linked on the website.

## Troubleshooting

- If an image cannot be downloaded or no face is detected, the script will print a warning and use a fallback crop.
- Make sure you have internet access for downloads.

## License

MIT License. See [LICENSE](LICENSE).
