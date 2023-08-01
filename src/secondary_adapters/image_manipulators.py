"""TODO"""
from abc import ABC
from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from pillow_heif import register_heif_opener

register_heif_opener()


@dataclass
class ImageManipulator(ABC):
    """TODO"""

    image_contents: BytesIO
    opened: bool = False

    def __enter__(self):
        """TODO"""
        self.opened = True

    def __exit__(self, exc_type, exc_value, traceback):
        """TODO"""
        self.opened = False

    @staticmethod
    def assert_opened(inner_func):
        """TODO"""

        def wrapper(*args, **kwargs):
            if not args[0].opened:
                raise ImageManipulatorNotOpenedError()
            return inner_func(*args, **kwargs)

        return wrapper

    @assert_opened
    def resize_image(self, width: int, height: int):
        """TODO"""
        raise NotImplementedError

    @assert_opened
    def write_text_on_image(self, text: str, x_coord: int, y_coord: int):
        """TODO"""
        raise NotImplementedError

    @assert_opened
    def save_image_as_jpeg(self, output_path: str):
        """TODO"""
        raise NotImplementedError


class PillowImageManipulator(ImageManipulator):
    """TODO"""

    def __init__(self, image_contents: BytesIO):
        """TODO"""
        super().__init__(image_contents)
        self._image = None

    def __enter__(self):
        """TODO"""
        super().__enter__()
        self._image = Image.open(self.image_contents)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """TODO"""
        # TODO: WHat to do with these 3 args?
        self._image.close()
        super().__exit__(exc_type, exc_value, traceback)

    @ImageManipulator.assert_opened
    def resize_image(self, width: int, height: int):
        """TODO"""
        self._image = self._image.resize((width, height))

    @ImageManipulator.assert_opened
    def write_text_on_image(self, text: str, x_coord: int, y_coord: int):
        """TODO"""
        # TODO: Use environment variable for font path
        font_size = 100
        draw = ImageDraw.Draw(self._image)
        draw.text(
            (x_coord, y_coord),
            text,
            font=ImageFont.truetype(
                "/Users/joshclark/Documents/selfie-movie-maker/OpenSans-Regular.ttf",
                font_size,
            ),
            stroke_fill="black",
            stroke_width=2,
        )

    @ImageManipulator.assert_opened
    def save_image_as_jpeg(self, output_path: str):
        """TODO"""
        self._image.convert("RGB")  # TODO: Is this necessary?
        self._image.save(output_path, "jpeg")


class ImageManipulatorNotOpenedError(Exception):
    """TODO"""

    def __init__(self):
        """TODO"""
        super().__init__("ImageManipulator not opened")


if __name__ == "__main__":
    with open(
        "/Users/joshclark/Documents/selfie-movie-maker/heics/IMG_0096.HEIC", "rb"
    ) as f:
        with PillowImageManipulator(BytesIO(f.read())) as image_manipulator:
            image_manipulator.resize_image(600, 800)
            image_manipulator.write_text_on_image("Hello World!", 25, 0)
            image_manipulator.save_image_as_jpeg("test2.jpg")
