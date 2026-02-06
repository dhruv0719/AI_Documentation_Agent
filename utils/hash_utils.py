# utils/hash_utils.py
"""
Hash Utilities for Change Detection

Provides functions for:
- File content hashing
- Change detection between runs
- Metadata storage and retrieval
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

from utils.logger import get_logger

logger = get_logger(__name__)


class FileHashRecord(BaseModel):
    """Record of a file's hash and metadata"""
    file_path: str
    content_hash: str
    last_modified: datetime
    size_bytes: int


class HashMetadata(BaseModel):
    """Complete hash metadata for a project"""
    project_path: str
    last_scan: datetime = Field(default_factory=datetime.now)
    files: dict[str, FileHashRecord] = Field(default_factory=dict)


def calculate_file_hash(file_path: Path) -> Optional[str]:
    """
    Calculate SHA256 hash of file content.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Hex digest of the hash, or None if error
    """
    try:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.warning(f"Failed to hash {file_path}: {e}")
        return None


def calculate_content_hash(content: str) -> str:
    """Calculate SHA256 hash of string content"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_hash_metadata(metadata_path: Path) -> Optional[HashMetadata]:
    """Load hash metadata from file"""
    try:
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                data = json.load(f)
            return HashMetadata(**data)
    except Exception as e:
        logger.warning(f"Failed to load hash metadata: {e}")
    return None


def save_hash_metadata(metadata: HashMetadata, metadata_path: Path) -> bool:
    """Save hash metadata to file"""
    try:
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with open(metadata_path, "w") as f:
            json.dump(metadata.model_dump(mode="json"), f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Failed to save hash metadata: {e}")
        return False


def detect_changes(
    current_files: list[Path],
    metadata: Optional[HashMetadata]
) -> tuple[list[Path], list[Path], list[Path]]:
    """
    Detect changes between current files and stored metadata.
    
    Args:
        current_files: List of current file paths
        metadata: Previously stored hash metadata
    
    Returns:
        Tuple of (new_files, modified_files, deleted_files)
    """
    if metadata is None:
        return current_files, [], []
    
    new_files = []
    modified_files = []
    deleted_files = []
    
    current_paths = {str(f) for f in current_files}
    stored_paths = set(metadata.files.keys())
    
    # Find new files
    for file_path in current_files:
        path_str = str(file_path)
        if path_str not in stored_paths:
            new_files.append(file_path)
        else:
            # Check if modified
            current_hash = calculate_file_hash(file_path)
            if current_hash and current_hash != metadata.files[path_str].content_hash:
                modified_files.append(file_path)
    
    # Find deleted files
    for stored_path in stored_paths:
        if stored_path not in current_paths:
            deleted_files.append(Path(stored_path))
    
    return new_files, modified_files, deleted_files