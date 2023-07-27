"""TODO"""
from io import BytesIO
import os
from typing import Generator, Type

from src.secondary_adapters.image_format_readers import ImageFormatReader, WhatImageIFR
from src.secondary_adapters.image_manipulators import (
    ImageManipulator,
    PillowImageManipulator,
)
from src.secondary_adapters.image_metadata_readers import (
    ImageMetadataReader,
    HEICMetadataReader,
)


RESIZE_WIDTH = 600
RESIZE_HEIGHT = 800
TEXT_X_COORD = 25
TEXT_Y_COORD = 0


def prepare_images(
    input_path: str,
    output_path: str,
    image_format_reader: Type[ImageFormatReader],
    image_manipulator: Type[ImageManipulator],
) -> None:
    """TODO

    Notes:
        - Images will be prepared in sorted order.
        - All images must be of the same format.
    """
    # TODO: Confirm output dir exists?

    # Get all images to be prepared
    images = sorted(listdir_no_hidden(input_path))

    # Get image format from first image
    fmt = get_image_format(os.path.join(input_path, images[0]), image_format_reader)

    # Get appropriate metadata reader
    if fmt == "heic":
        metadata_reader = HEICMetadataReader
    else:
        raise UnsupportedImageFormatError(fmt)

    # Get length for filename padding
    filename_length = len(str(len(images)))

    # Prepare each image
    for image_index, image in enumerate(images):
        with open(os.path.join(input_path, image), "rb") as image_fp:
            image_contents = image_fp.read()

        prepare_image(
            image_contents,
            os.path.join(output_path, f"{image_index:0{filename_length}}.jpeg"),
            metadata_reader,
            image_manipulator,
        )


def listdir_no_hidden(path: str) -> Generator[str, None, None]:
    """TODO

    This function was created to ignore files like .DS_Store.
    """
    for dir_entry in os.listdir(path):
        if not dir_entry.startswith("."):
            yield dir_entry


def get_image_format(
    image_path: str, image_format_reader: Type[ImageFormatReader]
) -> str:
    """TODO"""
    with open(os.path.join(image_path), "rb") as image:
        image_contents = image.read()

    return image_format_reader.get_image_format(image_contents)


def prepare_image(
    image_contents: bytes,
    output_path: str,
    metadata_reader: Type[ImageMetadataReader],
    image_manipulator: Type[ImageManipulator],
) -> None:
    """TODO"""
    # Get the date
    date = metadata_reader.get_image_date(image_contents)

    # Do image manipulation
    with image_manipulator(BytesIO(image_contents)) as manipulator:
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


if __name__ == "__main__":
    # with open(
    #     "/Users/joshclark/Documents/selfie-movie-maker/heics/IMG_0096.HEIC", "rb"
    # ) as x_image_fp:
    #     prepare_image(
    #         x_image_fp.read(),
    #         "test_3.jpeg",
    #         HEICMetadataReader,
    #         PillowImageManipulator,
    #     )

    prepare_images(
        "/Users/joshclark/Documents/selfie-movie-maker/heics",
        "/Users/joshclark/Documents/selfie-movie-maker/test_jpegs",
        WhatImageIFR,
        PillowImageManipulator,
    )
