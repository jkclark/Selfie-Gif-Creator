from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from src.ports.image_manipulator import (
    ImageManipulator,
    ImageManipulatorFontPathNotSetError,
)


class PillowImageManipulator(ImageManipulator):
    """An image manipulator that uses Pillow."""

    def __init__(self, image_path: Path):
        super().__init__(image_path)
        self._image = None

    def __enter__(self):
        super().__enter__()
        self._image = Image.open(self.image_path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
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
        """Resize the image to the given width and height."""
        self._image = self._image.resize((width, height))

    @ImageManipulator.assert_opened
    def write_text_on_image(self, text: str, x_coord: int, y_coord: int):
        """Write the given text on the image at the given coordinates."""
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
        """Save the image as a jpeg."""
        self._image.convert("RGB")
        self._image.save(output_path, "jpeg")
