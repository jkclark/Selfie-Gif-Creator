from pathlib import Path

import whatimage

from src.ports.image_format_reader import ImageFormatReader


class WhatImageIFR(ImageFormatReader):
    """An image-format reader that uses the whatimage library."""

    @staticmethod
    def get_image_format(image_path: Path) -> str:
        """Return the image format of an image."""
        with open(image_path, "rb") as image_fp:
            image_contents = image_fp.read()

        return whatimage.identify_image(image_contents)
