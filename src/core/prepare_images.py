"""TODO"""
from datetime import datetime
from pathlib import Path
from typing import Generator, Type

from src.ports.image_format_reader import ImageFormatReader
from src.ports.image_manipulator import ImageManipulator
from src.secondary_adapters.image_metadata_readers import (
    HEICMetadataReader,
    JPEGMetadataReader,
)

IMAGE_FORMAT_TO_METADATA_READER = {
    "heic": HEICMetadataReader,
    "jpeg": JPEGMetadataReader,
}


DATE_STR_FORMAT = "%m/%d/%Y"
RESIZE_WIDTH = 600
RESIZE_HEIGHT = 800
TEXT_X_COORD = 25
TEXT_Y_COORD = 0


def prepare_dated_images(
    input_path: Path,
    input_date_format: str,
    image_manipulator: Type[ImageManipulator],
    output_path: Path,
) -> None:
    """Prepare all images in a directory, where images are titled by date.

    Images must be titled with date in the format specified by input_date_format.

    Args:
        input_path: Path to directory containing images to be prepared
        input_date_format: Format of date in image titles
        image_manipulator: ImageManipulator subclass to use for image manipulation
        output_path: Path to directory in which save prepared images

    Images are sorted by title (date) increasing.
    """
    if not output_path.exists():
        raise FileNotFoundError(
            f"Prepared-image directory does not exist: {output_path}"
        )

    for image_index, image in enumerate(sorted(listdir_no_hidden(input_path))):
        prepare_image(
            image,
            datetime.strptime(image.stem, input_date_format).strftime(DATE_STR_FORMAT),
            image_manipulator,
            output_path / f"{image_index:04}.jpeg",
        )


def prepare_images(
    input_path: Path,
    image_format_reader: Type[ImageFormatReader],
    image_manipulator: Type[ImageManipulator],
    output_path: Path,
) -> None:
    """Prepare all images in a directory for use in a movie.

    The input directory should contain only images to be prepared.
    """
    if not output_path.exists():
        raise FileNotFoundError(
            f"Prepared-image directory does not exist: {output_path}"
        )

    # Get all images sorted by date increasing
    images_and_dates = sorted(
        [
            (image, get_image_date(image, image_format_reader))
            for image in listdir_no_hidden(input_path)
        ],
        key=lambda image_and_date: image_and_date[1],
    )

    # Get length of filename padding
    filename_length = len(str(len(images_and_dates)))

    # Prepare image
    for image_index, (image, date) in enumerate(images_and_dates):
        prepare_image(
            image,
            date.strftime(DATE_STR_FORMAT),
            image_manipulator,
            output_path / f"{image_index:0{filename_length}}.jpeg",
        )


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


def listdir_no_hidden(path: Path) -> Generator[str, None, None]:
    """Yield all non-hidden files in a directory.

    Yielded path names include the directory name.

    This function was created to ignore files like .DS_Store.
    """
    for dir_entry in path.iterdir():
        if dir_entry.is_file() and not dir_entry.name.startswith("."):
            yield dir_entry


def prepare_image(
    image_path: Path,
    date: str,
    image_manipulator: Type[ImageManipulator],
    output_path: Path,
) -> None:
    """TODO"""

    # Do image manipulation
    with image_manipulator(image_path) as manipulator:
        # Orient image correctly
        manipulator.reorient_image()

        # Resize image
        manipulator.resize_image(RESIZE_WIDTH, RESIZE_HEIGHT)

        # Overlay image with date
        manipulator.write_text_on_image(date, TEXT_X_COORD, TEXT_Y_COORD)

        # Convert image to JPEG
        manipulator.save_image_as_jpeg(output_path)


class UnsupportedImageFormatError(Exception):
    """TODO"""

    def __init__(self, fmt: str) -> None:
        super().__init__(f"Unsupported image format: {fmt}")
