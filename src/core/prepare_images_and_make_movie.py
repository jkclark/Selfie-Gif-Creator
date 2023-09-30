"""TODO"""
from typing import Type

from src.core.make_movie import append_images_to_movie, make_movie_from_scratch
from src.core.prepare_images import prepare_images
from src.secondary_adapters.image_format_readers import ImageFormatReader
from src.secondary_adapters.image_manipulators import ImageManipulator
from src.secondary_adapters.video_processors import VideoProcessor


def prepare_images_and_make_movie(
    input_path: str,
    temp_folder: str,
    output_path: str,
    image_format_reader: Type[ImageFormatReader],
    image_manipulator: Type[ImageManipulator],
    video_processor: Type[VideoProcessor],
) -> None:
    """TODO"""
    prepare_images(input_path, temp_folder, image_format_reader, image_manipulator)
    make_movie_from_scratch(temp_folder, output_path, video_processor)


def prepare_images_and_append_to_movie(
    images_path: str,
    temp_folder: str,
    movie_path: str,
    image_format_reader: Type[ImageFormatReader],
    image_manipulator: Type[ImageManipulator],
    video_processor: Type[VideoProcessor],
    output_path: str = "",
) -> None:
    """TODO

    NOTE: This will prepare every file in the images_path.
    """
    prepare_images(images_path, temp_folder, image_format_reader, image_manipulator)
    append_images_to_movie(
        temp_folder,
        movie_path,
        video_processor,
        output_path if output_path else movie_path,
    )
