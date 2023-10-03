"""TODO"""
from pathlib import Path
from typing import Generator, Type

from src.secondary_adapters.image_format_readers import ImageFormatReader
from src.secondary_adapters.image_manipulators import ImageManipulator
from src.secondary_adapters.image_metadata_readers import (
    HEICMetadataReader,
    ImageMetadataReader,
)

RESIZE_WIDTH = 600
RESIZE_HEIGHT = 800
TEXT_X_COORD = 25
TEXT_Y_COORD = 0


def prepare_images(
    input_path: Path,
    output_path: Path,
    image_format_reader: Type[ImageFormatReader],
    image_manipulator: Type[ImageManipulator],
) -> None:
    """TODO

    Notes:
        - Images will be prepared in sorted order.
        - All images must be of the same format.
    """
    if not output_path.exists():
        raise FileNotFoundError(
            f"Prepared-image directory does not exist: {output_path}"
        )

    # Get all images to be prepared
    images = sorted(listdir_no_hidden(input_path))

    # Get image format from first image
    fmt = image_format_reader.get_image_format(images[0])

    # Get appropriate metadata reader
    if fmt == "heic":
        metadata_reader = HEICMetadataReader
    else:
        raise UnsupportedImageFormatError(fmt)

    # Get length for filename padding
    filename_length = len(str(len(images)))

    # Prepare each image
    for image_index, image in enumerate(images):
        prepare_image(
            image,
            output_path / f"{image_index:0{filename_length}}.jpeg",
            metadata_reader,
            image_manipulator,
        )


def listdir_no_hidden(path: Path) -> Generator[str, None, None]:
    """Yield all non-hidden files in a directory.

    Yielded path names include the directory name.

    This function was created to ignore files like .DS_Store.
    """
    for dir_entry in path.iterdir():
        if not dir_entry.name.startswith("."):
            yield dir_entry


def prepare_image(
    image_path: Path,
    output_path: Path,
    metadata_reader: Type[ImageMetadataReader],
    image_manipulator: Type[ImageManipulator],
) -> None:
    """TODO"""
    # Get the date
    date = metadata_reader.get_image_date(image_path)

    # Do image manipulation
    with image_manipulator(image_path) as manipulator:
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
