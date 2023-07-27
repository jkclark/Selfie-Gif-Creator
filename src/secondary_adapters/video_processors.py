"""TODO"""
from abc import ABC, abstractmethod
import os


class VideoProcessor(ABC):
    """TODO"""

    @staticmethod
    @abstractmethod
    def create_movie_from_images(images_path: str, output_path: str) -> None:
        """TODO"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def append_image_to_movie(
        image_path: str, movie_path: str, output_path: str = ""
    ) -> None:
        """TODO"""
        raise NotImplementedError


class FFmpegVP(VideoProcessor):
    """TODO

    This link is a concise guide to the ffmpeg flags:
    https://gist.github.com/tayvano/6e2d456a9897f55025e25035478a3a50
    """

    FRAMERATE = 15  # Literally, the number of images to be shown per second

    @staticmethod
    def create_movie_from_images(images_path: str, output_path: str) -> None:
        """TODO"""
        os.system(
            " ".join(
                (
                    "ffmpeg",
                    f"-r {FFmpegVP.FRAMERATE}",
                    "-f image2",
                    "-s 600x800",
                    f'-i "{images_path}/*.jpeg"',
                    "-vcodec libx264",
                    "-crf 25",
                    f"{output_path}.mp4",
                )
            )
        )

    @staticmethod
    def append_iamge_to_movie(
        image_path: str, movie_path: str, output_path: str = ""
    ) -> None:
        """TODO"""
