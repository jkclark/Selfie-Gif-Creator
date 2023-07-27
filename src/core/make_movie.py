"""TODO"""
from typing import Type

from src.secondary_adapters.video_processors import VideoProcessor


def make_movie_from_scratch(
    images_path: str,
    output_path: str,
    video_processor: Type[VideoProcessor],
):
    """Concatenate images into a movie."""
    video_processor.create_movie_from_images(images_path, output_path)


def add_image_to_movie(
    image_path: str,
    movie_path: str,
    video_processor: Type[VideoProcessor],
    output_path: str = "",
) -> None:
    """Append an image to a movie."""
    if output_path == "":
        output_path = movie_path

    video_processor.append_image_to_movie(image_path, movie_path, output_path)
