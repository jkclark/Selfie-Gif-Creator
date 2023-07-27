"""TODO"""
import os
from typing import Type

from src.core.make_movie import add_image_to_movie, make_movie_from_scratch
from src.core.prepare_images import prepare_image, prepare_images
from src.secondary_adapters.image_format_readers import (
    ImageFormatReader,
    WhatImageIFR,
)
from src.secondary_adapters.image_manipulators import (
    ImageManipulator,
    PillowImageManipulator,
)
from src.secondary_adapters.image_metadata_readers import (
    HEICMetadataReader,
    ImageMetadataReader,
)
from src.secondary_adapters.video_processors import FFmpegVP, VideoProcessor


def prepare_images_and_make_movie(
    input_path: str,
    output_path: str,
    image_format_reader: Type[ImageFormatReader],
    image_manipulator: Type[ImageManipulator],
    video_processor: Type[VideoProcessor],
) -> None:
    """TODO"""
    jpeg_dir = "./test_jpegs"
    prepare_images(input_path, jpeg_dir, image_format_reader, image_manipulator)
    make_movie_from_scratch(jpeg_dir, output_path, video_processor)


def prepare_image_and_append_to_movie(
    image_path: str,
    movie_path: str,
    metadata_reader: Type[ImageMetadataReader],
    image_manipulator: Type[ImageManipulator],
    video_processor: Type[VideoProcessor],
    output_path: str = "",
) -> None:
    """TODO"""
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    prepared_image_path = os.path.join("./test_jpegs", "image_to_append.jpg")
    prepare_image(
        image_bytes,
        prepared_image_path,
        metadata_reader,
        image_manipulator,
    )
    add_image_to_movie(
        prepared_image_path,
        movie_path,
        video_processor,
        output_path if output_path else movie_path,
    )


if __name__ == "__main__":
    # prepare_images_and_make_movie(
    #     input_path="./test_heics",
    #     output_path="./test_output.mp4",
    #     image_format_reader=WhatImageIFR,
    #     image_manipulator=PillowImageManipulator,
    #     video_processor=FFmpegVP,
    # )

    prepare_image_and_append_to_movie(
        "/Users/joshclark/Documents/selfie-movie-maker/test_heics/IMG_0217.HEIC",
        "./test_output.mp4",
        HEICMetadataReader,
        PillowImageManipulator,
        FFmpegVP,
        "./test_output_appended.mp4",
    )
