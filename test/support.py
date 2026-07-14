"""Shared test helpers that keep test artifacts inside the workspace."""

import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


TEST_TEMP_ROOT = Path(__file__).parent / ".tmp"


@contextmanager
def temporary_project() -> Iterator[Path]:
    """Create an isolated project directory in a writable test location."""
    TEST_TEMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=TEST_TEMP_ROOT) as directory:
        yield Path(directory)
