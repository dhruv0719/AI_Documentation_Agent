# utils/file_utils.py
"""
File Utility Functions

Provides helper functions for:
- File reading and writing
- Path manipulation
- Content validation
"""

from pathlib import Path
from typing import Optional
import aiofiles
import os

from utils.logger import get_logger

logger = get_logger(__name__)


def read_file_content(file_path: Path) -> Optional[str]:
    """
    Read and return file content.
    
    Args:
        file_path: Path to the file
    
    Returns:
        File content as string, or None if error
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")
            return None
    except Exception as e:
        logger.warning(f"Failed to read {file_path}: {e}")
        return None


async def read_file_async(file_path: Path) -> Optional[str]:
    """Async version of file reading"""
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            return await f.read()
    except Exception as e:
        logger.warning(f"Failed to read {file_path}: {e}")
        return None


def write_file_content(file_path: Path, content: str) -> bool:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file
        content: Content to write
    
    Returns:
        True if successful, False otherwise
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Failed to write {file_path}: {e}")
        return False


async def write_file_async(file_path: Path, content: str) -> bool:
    """Async version of file writing"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)
        return True
    except Exception as e:
        logger.error(f"Failed to write {file_path}: {e}")
        return False


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes"""
    try:
        return file_path.stat().st_size
    except Exception:
        return 0


def is_binary_file(file_path: Path) -> bool:
    """Check if a file is binary"""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(8192)
            return b"\x00" in chunk
    except Exception:
        return True


def get_relative_path(file_path: Path, base_path: Path) -> str:
    """Get relative path from base path"""
    try:
        return str(file_path.relative_to(base_path))
    except ValueError:
        return str(file_path)


def count_lines(content: str) -> int:
    """Count number of lines in content"""
    return len(content.splitlines())