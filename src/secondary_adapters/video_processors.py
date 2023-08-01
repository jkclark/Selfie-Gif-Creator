"""TODO"""
from abc import ABC, abstractmethod
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile


class VideoProcessor(ABC):
    """TODO"""

    @staticmethod
    @abstractmethod
    def create_movie_from_images(images_path: str, output_path: str) -> None:
        """TODO"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def append_images_to_movie(
        images_path: str,
        movie_path: str,
        output_path: str,
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
        """TODO

        NOTE: In order to specify just a folder (and not a glob pattern),
              the ffmpeg command below already includes "*.jpeg". This means
              we'd have to change this command to use a different extension.

        TODO: Explain ffmpeg options used here
        """
        subprocess.run(
            [
                "ffmpeg",
                "-r",
                f"{FFmpegVP.FRAMERATE}",
                "-f",
                "image2",
                "-s",
                "600x800",
                "-pattern_type",
                "glob",
                "-i",
                f"{images_path}/*.jpeg",
                "-vcodec",
                "libx264",
                "-crf",
                "25",
                f"{output_path}",
            ],
            check=True,
        )

    @staticmethod
    def append_images_to_movie(
        images_path: str,
        movie_path: str,
        output_path: str,
    ) -> None:
        """Add any number of images to the end of a movie.

        The original idea was to use a command like the one found here:
        https://video.stackexchange.com/a/17229, but it turns out that there
        were issues with the video's duration using this method. This method now
        instead uses the concat demuxer to concatenate two separate movies
        together. The first movie is the original movie, and the second movie is
        a movie that is created from the images that are to be appended.

        NOTE: It would seem that the two movies *must* be in the same directory
              in order for this to work.

        TODO: Explain ffmpeg options used here
        """
        # Get the folder where the movie is located (required for ffmpeg concat)
        temp_movie_path = Path(movie_path).parent / "temp.mp4"

        # Create a movie from the images to be appended
        FFmpegVP.create_movie_from_images(
            images_path,
            temp_movie_path,
        )

        # Create temporary file to store ffmpeg concat instructions
        with NamedTemporaryFile() as temp_file:
            temp_file.write(
                f"file '{movie_path}'\nfile {temp_movie_path}".encode("utf-8")
            )

            # Reset the file pointer to the beginning of the file
            temp_file.seek(0)

            # Concatenate the two movies
            subprocess.run(
                [
                    "ffmpeg",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    f"{temp_file.name}",
                    "-c",
                    "copy",
                    f"{output_path}",
                ],
                check=True,
            )

        # Delete the temporary movie
        temp_movie_path.unlink()
