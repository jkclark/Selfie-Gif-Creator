"""TODO"""
from typing import Type

from src.core.make_movie import add_images_to_movie, make_movie_from_scratch
from src.core.prepare_images import prepare_images
from src.secondary_adapters.image_format_readers import (
    ImageFormatReader,
)
from src.secondary_adapters.image_manipulators import (
    ImageManipulator,
)
from src.secondary_adapters.video_processors import VideoProcessor


def prepare_images_and_make_movie(
    input_path: str,
    output_path: str,
    image_format_reader: Type[ImageFormatReader],
    image_manipulator: Type[ImageManipulator],
    video_processor: Type[VideoProcessor],
) -> None:
    """TODO"""
    # TODO: Get rid of this and use /tmp or something
    jpeg_dir = "/Users/joshclark/Documents/selfie-movie-maker/test_jpegs"
    prepare_images(input_path, jpeg_dir, image_format_reader, image_manipulator)
    make_movie_from_scratch(jpeg_dir, output_path, video_processor)


def prepare_images_and_append_to_movie(
    images_path: str,
    movie_path: str,
    image_format_reader: Type[ImageFormatReader],
    image_manipulator: Type[ImageManipulator],
    video_processor: Type[VideoProcessor],
    output_path: str = "",
) -> None:
    """TODO

    NOTE: This will prepare every file in the images_path.
    """
    # TODO: Get rid of this and use /tmp or something
    jpeg_dir = "/Users/joshclark/Documents/selfie-movie-maker/test_jpegs"
    prepare_images(images_path, jpeg_dir, image_format_reader, image_manipulator)
    add_images_to_movie(
        jpeg_dir,
        movie_path,
        video_processor,
        output_path if output_path else movie_path,
    )
