"""Central logging setup for command-line and library consumers."""

import logging


def configure_logging(level: str = "INFO", verbose: bool = False) -> None:
    """Configure DocAgent logging without adding duplicate handlers."""
    resolved_level = logging.DEBUG if verbose else getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=resolved_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
