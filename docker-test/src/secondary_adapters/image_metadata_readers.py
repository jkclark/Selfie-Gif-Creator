"""TODO"""
import io
from abc import ABC, abstractmethod
from datetime import datetime

import exifread
import pyheif


class ImageMetadataReader(ABC):
    """TODO"""

    DATE_OUTPUT_FORMAT = "%m/%d/%Y"

    @staticmethod
    @abstractmethod
    def get_image_date(image_contents: bytes) -> str:
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
    def get_image_date(image_contents: bytes) -> str:
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


class NoEXIFDataError(Exception):
    """TODO"""


class DateNotFoundError(Exception):
    """TODO"""
