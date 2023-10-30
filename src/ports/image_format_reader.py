from abc import ABC, abstractmethod
from pathlib import Path


class ImageFormatReader(ABC):
    """An interface for image-format readers."""

    @staticmethod
    @abstractmethod
    def get_image_format(image_path: Path) -> str:
        """TODO"""
        raise NotImplementedError
