"""A module for determining images' dates."""
from datetime import datetime
from pathlib import Path
from typing import Dict, Type

from src.ports.image_format_reader import ImageFormatReader
from src.ports.image_metadata_reader import ImageMetadataReader
from src.ports.supported_image_formats import (
    SupportedImageFormat,
    UnsupportedImageFormatError,
)


def get_image_date(
    image_path: Path,
    image_format_reader: Type[ImageFormatReader],
    formats_to_metadata_readers: Dict[SupportedImageFormat, Type[ImageMetadataReader]],
) -> datetime:
    """Get an image's date."""
    # Get the image's format
    fmt = image_format_reader.get_image_format(image_path)

    # Return the image's date
    try:
        return formats_to_metadata_readers[fmt].get_image_date(image_path)
    except KeyError:
        raise UnsupportedImageFormatError(f"Unsupported image format: {fmt}")
