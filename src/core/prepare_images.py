"""This module contains functions for writing on images."""
from datetime import datetime
from pathlib import Path
from typing import Generator, Type

from src.ports.image_manipulator import ImageManipulator

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


def prepare_image(
    image_path: Path,
    date: str,
    image_manipulator: Type[ImageManipulator],
    output_path: Path,
) -> None:
    """Write a date on an image and save it as a jpeg."""

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


def listdir_no_hidden(path: Path) -> Generator[str, None, None]:
    """Yield all non-hidden files in a directory.

    Yielded path names include the directory name.

    This function was created to ignore files like .DS_Store.
    """
    for dir_entry in path.iterdir():
        if dir_entry.is_file() and not dir_entry.name.startswith("."):
            yield dir_entry
