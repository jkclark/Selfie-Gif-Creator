"""TODO"""
import shutil
from pathlib import Path

TMP_DIR = "/tmp/selfie-movie-maker"


def use_tmp_dir(inner_func):
    """Make a temporary directory for the duration of the function."""

    def wrapper(*args, **kwargs):
        Path(TMP_DIR).mkdir()

        inner_func(*args, **kwargs)

        shutil.rmtree(TMP_DIR)

    return wrapper
