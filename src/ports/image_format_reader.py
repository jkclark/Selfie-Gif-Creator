from abc import ABC, abstractmethod
from pathlib import Path

from src.ports.supported_image_formats import SupportedImageFormat


class ImageFormatReader(ABC):
    """An interface for image-format readers."""

    @staticmethod
    @abstractmethod
    def get_image_format(image_path: Path) -> SupportedImageFormat:
        """Get an image's format."""
        raise NotImplementedError
