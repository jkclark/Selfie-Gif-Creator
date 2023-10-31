from pathlib import Path

import whatimage

from src.ports.image_format_reader import ImageFormatReader
from src.ports.supported_image_formats import (
    SupportedImageFormat,
    UnsupportedImageFormatError,
)


class WhatImageIFR(ImageFormatReader):
    """An image-format reader that uses the whatimage library."""

    @staticmethod
    def get_image_format(image_path: Path) -> SupportedImageFormat:
        """Return the image format of an image."""
        with open(image_path, "rb") as image_fp:
            image_contents = image_fp.read()

        fmt = whatimage.identify_image(image_contents)
        if fmt == "jpeg":
            return SupportedImageFormat.JPEG
        if fmt == "heic":
            return SupportedImageFormat.HEIC

        raise UnsupportedImageFormatError(fmt)
