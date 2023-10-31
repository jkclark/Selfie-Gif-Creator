"""A module for determining images' dates."""
from datetime import datetime
from pathlib import Path
from typing import Type

from src.ports.image_format_reader import ImageFormatReader
from src.secondary_adapters.image_metadata_readers import (
    HEICMetadataReader,
    JPEGMetadataReader,
)

IMAGE_FORMAT_TO_METADATA_READER = {
    "heic": HEICMetadataReader,
    "jpeg": JPEGMetadataReader,
}


def get_image_date(
    image_path: Path,
    image_format_reader: Type[ImageFormatReader],
) -> datetime:
    """Get an image's date."""
    # Get the image's format
    fmt = image_format_reader.get_image_format(image_path)

    # Get appropriate metadata reader
    try:
        metadata_reader = IMAGE_FORMAT_TO_METADATA_READER[fmt]
    except KeyError as key_error:
        raise UnsupportedImageFormatError(fmt) from key_error

    # Return the image's date
    return metadata_reader.get_image_date(image_path)


class UnsupportedImageFormatError(Exception):
    """An error thrown when an trying to operate on an image with an unsupported format."""

    def __init__(self, fmt: str) -> None:
        super().__init__(f"Unsupported image format: {fmt}")
