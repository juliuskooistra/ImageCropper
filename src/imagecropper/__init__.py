"""ImageCropper — download portrait images and crop them into circular/square PNGs.

Public API
----------
    from imagecropper import crop_and_save_one, crop_folder, crop_specific_files
    from imagecropper import download
"""

from importlib import import_module
from typing import TYPE_CHECKING

__version__ = "0.1.0"

# Public name -> submodule that defines it (imported lazily on first access).
_EXPORTS = {
    "DIMENSIONS": "crop_images",
    "SHAPES": "crop_images",
    "crop_and_save_one": "crop_images",
    "crop_folder": "crop_images",
    "crop_specific_files": "crop_images",
    "download": "find_images",
}

__all__ = [*_EXPORTS, "__version__"]


def __getattr__(name: str):
    """Resolve public API names lazily (PEP 562).

    Importing submodules on demand keeps ``python -m imagecropper.<module>``
    free of runpy's "found in sys.modules" RuntimeWarning.
    """
    try:
        module = _EXPORTS[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
    return getattr(import_module(f".{module}", __name__), name)


def __dir__() -> list[str]:
    return sorted(__all__)


if TYPE_CHECKING:  # let IDEs and type checkers see the re-exports
    from .crop_images import (
        DIMENSIONS,
        SHAPES,
        crop_and_save_one,
        crop_folder,
        crop_specific_files,
    )
    from .find_images import download
