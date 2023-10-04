"""TODO"""
from abc import ABC
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()


class ImageManipulator(ABC):
    """TODO"""

    # This must be set before instantiating the class
    font_path = None

    def __init__(self, image_path: Path):
        """TODO"""
        self.image_path = image_path
        self.opened = False

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
    def reorient_image(self):
        """Rotate the image to the correct orientation."""
        raise NotImplementedError

    @assert_opened
    def resize_image(self, width: int, height: int):
        """TODO"""
        raise NotImplementedError

    @assert_opened
    def write_text_on_image(self, text: str, x_coord: int, y_coord: int):
        """TODO"""
        # NOTE: This check is duplicated -- subclasses write the same code.
        #       How can we have this code in one place?
        if not self.font_path:
            raise ImageManipulatorFontPathNotSetError()

        raise NotImplementedError

    @assert_opened
    def save_image_as_jpeg(self, output_path: Path):
        """TODO"""
        raise NotImplementedError


class PillowImageManipulator(ImageManipulator):
    """TODO"""

    def __init__(self, image_path: Path):
        """TODO"""
        super().__init__(image_path)
        self._image = None

    def __enter__(self):
        """TODO"""
        super().__enter__()
        self._image = Image.open(self.image_path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """TODO"""
        # TODO: What to do with these 3 args?
        self._image.close()
        super().__exit__(exc_type, exc_value, traceback)

    @ImageManipulator.assert_opened
    def reorient_image(self):
        """Rotate the image to the correct orientation.

        See the following for more information:
        - Explanation of Exif/image orientation: https://jdhao.github.io/2019/07/31/image_rotation_exif_info/
        - PIL solution suggestion: https://github.com/python-pillow/Pillow/issues/4703#issuecomment-645219973
        - PIL.ImageOps.exif_transpose: https://pillow.readthedocs.io/en/stable/reference/ImageOps.html#PIL.ImageOps.exif_transpose
        """
        self._image = ImageOps.exif_transpose(self._image)

    @ImageManipulator.assert_opened
    def resize_image(self, width: int, height: int):
        """TODO"""
        self._image = self._image.resize((width, height))

    @ImageManipulator.assert_opened
    def write_text_on_image(self, text: str, x_coord: int, y_coord: int):
        """TODO"""
        if not self.font_path:
            raise ImageManipulatorFontPathNotSetError()

        font_size = 100
        draw = ImageDraw.Draw(self._image)
        draw.text(
            (x_coord, y_coord),
            text,
            font=ImageFont.truetype(
                self.font_path,
                font_size,
            ),
            stroke_fill="black",
            stroke_width=2,
        )

    @ImageManipulator.assert_opened
    def save_image_as_jpeg(self, output_path: Path):
        """TODO"""
        self._image.convert("RGB")  # TODO: Is this necessary?
        self._image.save(output_path, "jpeg")


class ImageManipulatorNotOpenedError(Exception):
    """TODO"""

    def __init__(self):
        """TODO"""
        super().__init__("ImageManipulator not opened")


class ImageManipulatorFontPathNotSetError(Exception):
    """TODO"""

    def __init__(self):
        """TODO"""
        super().__init__("ImageManipulator.font_path not set")
