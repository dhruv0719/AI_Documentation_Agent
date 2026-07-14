"""Environment loading utilities.

The loader intentionally does not overwrite values supplied by the calling
environment.  This keeps local ``.env`` files convenient while allowing CI
and secret managers to remain authoritative.
"""

from pathlib import Path
from typing import Dict


def load_dotenv(project_root: Path, filename: str = ".env") -> Dict[str, str]:
    """Load simple ``KEY=VALUE`` entries from a project-local environment file.

    Returns only variables applied to ``os.environ``. Missing files are not an
    error. Lines beginning with ``#`` and optional ``export`` prefixes are
    supported; existing environment values are never replaced.
    """
    import os

    path = project_root / filename
    if not path.is_file():
        return {}

    loaded: Dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise ValueError(f"Invalid .env entry at {path}:{line_number}")

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or not key.replace("_", "").isalnum() or key[0].isdigit():
            raise ValueError(f"Invalid .env key at {path}:{line_number}")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"\"", "'"}:
            value = value[1:-1]
        if key not in os.environ:
            os.environ[key] = value
            loaded[key] = value

    return loaded
