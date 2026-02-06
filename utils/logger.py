# utils/logger.py
"""
Logging Configuration for Code Documentation Agent

Provides consistent logging across all modules with:
- Colored console output using Rich
- File logging support
- Configurable log levels
"""

import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
import logging

# Rich console for pretty output
console = Console()


def setup_logger(
    name: str = "code_doc_agent",
    level: str = "INFO",
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up and configure a logger instance.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path for file logging
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Rich console handler for pretty output
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True
    )
    rich_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(rich_handler)
    
    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )
        )
        logger.addHandler(file_handler)
    
    return logger


# Default logger instance
logger = setup_logger()


def get_logger(name: str = "code_doc_agent") -> logging.Logger:
    """Get or create a logger with the given name"""
    return logging.getLogger(name)