from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path


class ImageMetadataReader(ABC):
    """An ABC for a metadata reader for a specific image format."""

    @staticmethod
    @abstractmethod
    def get_image_date(image_path: Path) -> datetime:
        """Get an image's date."""
        raise NotImplementedError
