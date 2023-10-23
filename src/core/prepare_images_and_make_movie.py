"""TODO"""
from pathlib import Path
from typing import Type, Union

from src.core.make_movie import append_images_to_movie, make_movie_from_scratch
from src.core.prepare_images import prepare_dated_images, prepare_images
from src.secondary_adapters.image_format_readers import ImageFormatReader
from src.secondary_adapters.image_manipulators import ImageManipulator
from src.secondary_adapters.video_processors import VideoProcessor


def prepare_images_and_make_movie(
    input_path: Path,
    temp_folder: Path,
    image_format_reader: Type[ImageFormatReader],
    image_manipulator: Type[ImageManipulator],
    video_processor: Type[VideoProcessor],
    output_path: Path,
) -> None:
    """TODO"""
    prepare_images(input_path, image_format_reader, image_manipulator, temp_folder)
    make_movie_from_scratch(temp_folder, output_path, video_processor)


def prepare_images_and_append_to_movie(
    images_path: Path,
    input_date_format: str,
    temp_folder: Path,
    movie_path: Path,
    image_manipulator: Type[ImageManipulator],
    video_processor: Type[VideoProcessor],
    output_path: Union[Path, None] = None,
) -> None:
    """TODO

    NOTE: This will prepare every file in the images_path.
    """
    prepare_dated_images(images_path, input_date_format, image_manipulator, temp_folder)
    append_images_to_movie(
        temp_folder,
        movie_path,
        video_processor,
        output_path if output_path else movie_path,
    )
