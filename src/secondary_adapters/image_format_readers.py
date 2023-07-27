"""TODO"""
from abc import ABC, abstractmethod

import whatimage


class ImageFormatReader(ABC):
    """TODO"""

    @staticmethod
    @abstractmethod
    def get_image_format(image_contents: bytes) -> str:
        raise NotImplementedError


class WhatImageIFR(ImageFormatReader):
    """TODO"""

    @staticmethod
    def get_image_format(image_contents: bytes) -> str:
        """TODO"""
        return whatimage.identify_image(image_contents)
