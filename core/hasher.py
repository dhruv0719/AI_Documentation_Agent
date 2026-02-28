# core/hasher.py
"""This module provides utilities for hashing file contents to detect changes efficiently. It includes functions to generate hashes for individual files and batches of files, which can be used to compare against previous analyses and determine what has changed since the last run."""

import hashlib
from typing import List, Dict

class FileHasher:
    """Fast, reliable file hashing."""

    @staticmethod
    def hash_file(file_path: str) -> str:
        """
        Generate SHA-256 hash of file content.

        Args:
            file_path: Path to file

        Returns:
            Hexa string of hash (64 chars)
        """
        sha256 = hashlib.sha256() # Here we use SHA-256 for a good balance of speed and collision resistance. But for faster hashing, if we have 64-bits hardware then we will use the SHA‑512. It will increase speed by 50% compared to SHA‑256. But it will produce a longer hash (128 chars). 

        with open(file_path, "rb") as f:
            # Read in chunks to handle large files
            while chunk := f.read(8192):
                sha256.update(chunk)

        return sha256.hexdigest()
    
    @staticmethod
    def hash_files(file_paths: List[str]) -> Dict[str, str]:
        """
        Hash multiple files efficiently.
        
        Returns:
            Dict mapping file_path → hash
        """
        hashes = {}
        for file_path in file_paths:
            try:
                hashes[file_path] = FileHasher.hash_file(file_path)
            
            except Exception as e:
                print(f"Warning: Could not hash {file_path}: {e}")
        
        return hashes