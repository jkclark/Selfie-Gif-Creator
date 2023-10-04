"""TODO"""
from pathlib import Path
from typing import Type, Union

from src.secondary_adapters.video_processors import VideoProcessor


def make_movie_from_scratch(
    images_path: Path,
    video_processor: Type[VideoProcessor],
    output_path: Path,
):
    """Concatenate images into a movie."""
    video_processor.create_movie_from_images(images_path, output_path)


def append_images_to_movie(
    images_path: Path,
    movie_path: Path,
    video_processor: Type[VideoProcessor],
    output_path: Union[Path, None] = None,
) -> None:
    """Append any number of images to a movie."""
    if output_path == "":
        output_path = movie_path

    video_processor.append_images_to_movie(images_path, movie_path, output_path)
