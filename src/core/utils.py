"""TODO"""
import shutil
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def use_tmp_dir(dir_path: str):
    """Make a temporary directory for the duration of the block."""
    Path(dir_path).mkdir()

    yield

    shutil.rmtree(dir_path)
