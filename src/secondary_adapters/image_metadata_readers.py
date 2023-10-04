"""This file contains the secondary adapters for reading image metadata."""
import io
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import exifread
import pyheif
from PIL import Image
from PIL.ExifTags import TAGS


class ImageMetadataReader(ABC):
    """An ABC for image metadata readers."""

    @staticmethod
    @abstractmethod
    def get_image_date(image_path: Path) -> datetime:
        """Get an image's date."""
        raise NotImplementedError


class HEICMetadataReader(ImageMetadataReader):
    """A metadata reader for HEIC images."""

    DATE_INPUT_FORMAT = "%Y:%m:%d %H:%M:%S"

    @staticmethod
    def get_image_date(image_path: Path) -> datetime:
        with open(image_path, "rb") as image_fp:
            image_contents = image_fp.read()

        # https://github.com/carsales/pyheif#the-heiffile-object
        heif_file = pyheif.read_heif(image_contents)

        # Find EXIF data
        for metadatum in (metadata := heif_file.metadata or []):
            if metadatum["type"] == "Exif":
                fstream = io.BytesIO(metadatum["data"][6:])
                break
        else:
            raise NoEXIFDataError(f"No EXIF data found in {metadata}")

        # Extract date
        if "EXIF DateTimeOriginal" in (tags := exifread.process_file(fstream)):
            return datetime.strptime(
                str(tags["EXIF DateTimeOriginal"]), HEICMetadataReader.DATE_INPUT_FORMAT
            )

        raise DateNotFoundError


class JPEGMetadataReader(ImageMetadataReader):
    """A metadata reader for JPEG images."""

    DATE_INPUT_FORMAT = "%Y:%m:%d %H:%M:%S"

    @staticmethod
    def get_image_date(image_path: Path) -> datetime:
        with Image.open(image_path) as image:
            exifdata = image.getexif()

        for tag_id in exifdata:
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)
            if tag == "DateTime":
                return datetime.strptime(data, JPEGMetadataReader.DATE_INPUT_FORMAT)

        raise DateNotFoundError


class NoEXIFDataError(Exception):
    """An error raised when no EXIF data is found for an image."""


class DateNotFoundError(Exception):
    """An error raised when no date is found for an image."""
