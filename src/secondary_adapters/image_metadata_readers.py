"""TODO"""
import io
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import exifread
import pyheif
from PIL import Image
from PIL.ExifTags import TAGS


class ImageMetadataReader(ABC):
    """TODO"""

    DATE_OUTPUT_FORMAT = "%m/%d/%Y"

    @staticmethod
    @abstractmethod
    def get_image_date(image_path: Path) -> str:
        """TODO"""
        raise NotImplementedError

    @staticmethod
    def parse_and_format_date(date: str, input_format: str) -> str:
        """Convert date from input_format to DATE_OUTPUT_FORMAT."""
        return datetime.strptime(date, input_format).strftime(
            ImageMetadataReader.DATE_OUTPUT_FORMAT
        )


class HEICMetadataReader(ImageMetadataReader):
    """TODO"""

    DATE_INPUT_FORMAT = "%Y:%m:%d %H:%M:%S"

    @staticmethod
    def get_image_date(image_path: Path) -> str:
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
            return ImageMetadataReader.parse_and_format_date(
                str(tags["EXIF DateTimeOriginal"]), HEICMetadataReader.DATE_INPUT_FORMAT
            )

        raise DateNotFoundError


class JPEGMetadataReader(ImageMetadataReader):
    """A metadata reader for JPEG images."""

    DATE_INPUT_FORMAT = "%Y:%m:%d %H:%M:%S"

    @staticmethod
    def get_image_date(image_path: Path) -> str:
        with Image.open(image_path) as image:
            exifdata = image.getexif()

        for tag_id in exifdata:
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)
            if tag == "DateTime":
                return ImageMetadataReader.parse_and_format_date(
                    data, JPEGMetadataReader.DATE_INPUT_FORMAT
                )

        raise DateNotFoundError


class NoEXIFDataError(Exception):
    """TODO"""


class DateNotFoundError(Exception):
    """TODO"""
