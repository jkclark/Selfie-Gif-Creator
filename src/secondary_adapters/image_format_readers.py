"""TODO"""
from abc import ABC, abstractmethod
from pathlib import Path

import whatimage


class ImageFormatReader(ABC):
    """TODO"""

    @staticmethod
    @abstractmethod
    def get_image_format(image_path: Path) -> str:
        """TODO"""
        raise NotImplementedError


class WhatImageIFR(ImageFormatReader):
    """TODO"""

    @staticmethod
    def get_image_format(image_path: Path) -> str:
        """TODO"""
        with open(image_path, "rb") as image_fp:
            image_contents = image_fp.read()

        return whatimage.identify_image(image_contents)
