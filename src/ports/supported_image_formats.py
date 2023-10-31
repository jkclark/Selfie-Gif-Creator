"""This module lists the app's supported image formats."""
from enum import Enum, auto


class SupportedImageFormat(Enum):
    """An enumeration of supported image formats."""

    JPEG = auto()
    HEIC = auto()


class UnsupportedImageFormatError(Exception):
    """An error thrown when an trying to operate on an image with an unsupported format."""

    def __init__(self, fmt: str) -> None:
        super().__init__(f"Unsupported image format: {fmt}")
