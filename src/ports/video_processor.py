from abc import ABC, abstractmethod
from pathlib import Path


class VideoProcessor(ABC):
    """An interface for video processors."""

    @staticmethod
    @abstractmethod
    def create_movie_from_images(images_path: Path, output_path: Path) -> None:
        """Create a movie from a folder of images."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def append_images_to_movie(
        images_path: Path,
        movie_path: Path,
        output_path: Path,
    ) -> None:
        """Append images in a folder to a movie."""
        raise NotImplementedError
