"""TODO"""
from typing import Type

from src.core.make_movie import append_images_to_movie, make_movie_from_scratch
from src.core.prepare_images import prepare_images
from src.core.utils import use_tmp_dir
from src.secondary_adapters.image_format_readers import ImageFormatReader
from src.secondary_adapters.image_manipulators import ImageManipulator
from src.secondary_adapters.video_processors import VideoProcessor

# TODO: Make this an environment variable
TMP_DIR = "/tmp/selfie-movie-maker"


def prepare_images_and_make_movie(
    input_path: str,
    output_path: str,
    image_format_reader: Type[ImageFormatReader],
    image_manipulator: Type[ImageManipulator],
    video_processor: Type[VideoProcessor],
) -> None:
    """TODO"""
    with use_tmp_dir(TMP_DIR):
        prepare_images(input_path, TMP_DIR, image_format_reader, image_manipulator)
        make_movie_from_scratch(TMP_DIR, output_path, video_processor)


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
    with use_tmp_dir(TMP_DIR):
        prepare_images(images_path, TMP_DIR, image_format_reader, image_manipulator)
        append_images_to_movie(
            TMP_DIR,
            movie_path,
            video_processor,
            output_path if output_path else movie_path,
        )
