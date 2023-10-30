from abc import ABC
from pathlib import Path


class ImageManipulator(ABC):
    """An interface for image manipulators."""

    # This must be set before instantiating the class
    font_path = None

    def __init__(self, image_path: Path):
        self.image_path = image_path
        self.opened = False

    def __enter__(self):
        self.opened = True

    def __exit__(self, exc_type, exc_value, traceback):
        self.opened = False

    @staticmethod
    def assert_opened(inner_func):
        """A decorator to make sure that the image is opened before calling the inner function."""

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
        """Resize the image to the given width and height."""
        raise NotImplementedError

    @assert_opened
    def write_text_on_image(self, text: str, x_coord: int, y_coord: int):
        """Write the given text on the image at the given coordinates."""
        # NOTE: This check is duplicated -- subclasses write the same code.
        #       How can we have this code in one place?
        if not self.font_path:
            raise ImageManipulatorFontPathNotSetError()

        raise NotImplementedError

    @assert_opened
    def save_image_as_jpeg(self, output_path: Path):
        """Save the image as a jpeg."""
        raise NotImplementedError


class ImageManipulatorNotOpenedError(Exception):
    """An error thrown when an image manipulator is not opened before use."""

    def __init__(self):
        super().__init__("ImageManipulator not opened")


class ImageManipulatorFontPathNotSetError(Exception):
    """An error thrown when an image manipulator's font path is not set before use."""

    def __init__(self):
        super().__init__("ImageManipulator.font_path not set")
