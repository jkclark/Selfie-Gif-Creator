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
                    "-pattern_type glob",
                    f'-i "{images_path}/*.jpeg"',
                    "-vcodec libx264",
                    "-crf 25",
                    f"{output_path}",
                )
            )
        )

    @staticmethod
    def append_image_to_movie(
        image_path: str,
        movie_path: str,
        output_path: str,
    ) -> None:
        """TODO

        This ffmpeg command is taken from this answer:
        https://video.stackexchange.com/a/17229

        As noted in the comments in the answer (and verified by me),
        ffmpeg will run forever if the output given is .mp4. So,
        we create the new movie as an mkv file and then convert it to mp4.
        """
        # TODO: Convert this to a real logger.warning call
        if not output_path.endswith(".mp4"):
            print("WARNING: output will be an mp4 file")

        output_path_no_extension = FFmpegVP._get_filename_without_extension(output_path)

        os.system(
            " ".join(
                (
                    f"ffmpeg -i {movie_path}",
                    f"-loop 1 -t 3 -i {image_path}",
                    "-f lavfi -t 3 -i anullsrc",
                    "-filter_complex '[0:v] [1:v] concat=n=2:v=1 [v]'",
                    "-c:v libx264 -strict -2 -map '[v]'",
                    f"{output_path_no_extension + '.mkv'}",
                )
            )
        )

        FFmpegVP._convert_mkv_to_mp4(output_path_no_extension)

        # Remove the mkv file
        os.remove(output_path_no_extension + ".mkv")

    @staticmethod
    def _get_filename_without_extension(path: str) -> str:
        """TODO

        Taken from this answer:
        https://stackoverflow.com/a/678242/3801865
        """
        return os.path.splitext(path)[0]

    @staticmethod
    def _convert_mkv_to_mp4(input_path_no_extension: str) -> None:
        """TODO

        This ffmpeg command is taken from the same answer as above:
        https://video.stackexchange.com/a/17229
        """
        # TODO: This produces a video that plays correctly but the
        #       duration is not correct. This needs to be fixed.
        # IDEA: Maybe we can create a movie out of the one frame,
        #       and then append it to the original movie, instead of
        #       trying to append the frame directly to the original movie.
        os.system(
            f"ffmpeg -i {input_path_no_extension + '.mkv'} -codec copy {input_path_no_extension + '.mp4'}"
        )
