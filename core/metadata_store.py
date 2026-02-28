# core/metadata_store.py
"""This module manages the persistent storage of project metadata, including loading and saving metadata to disk. It provides a simple interface for the rest of the system to access and update metadata about files and projects, ensuring that change detection and analysis can be performed efficiently across runs."""

import json
from pathlib import Path
from typing import Optional
from models.metadata import ProjectMetadata

class MetadataStore:
    """Persistent storage for project metadata."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.metadata_dir = self.project_root / ".docagent"
        self.metadata_file = self.metadata_dir / "metadata.json"

        # Create directory if it doesn't exist
        self.metadata_dir.mkdir(exist_ok=True)

    def load(self) -> Optional[ProjectMetadata]:
        """
        Load metadata from disk.
        
        Returns:
            ProjectMetadata if exists, None if first run
        """
        if not self.metadata_file.exists():
            return None
        
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ProjectMetadata.from_json(data)

        except Exception as e:
            print(f"Error: Could not load metadata: {e}")
            return None
        
    def save(self, metadata: ProjectMetadata):
        """Save metadata to disk."""
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata.to_json(), f, indent=2)

        except Exception as e:
            print(f"Error: Could not save metadata: {e}")

    def clear(self):
        """Delete metadata (force full reanalysis)."""
        if self.metadata_file.exists():
            self.metadata_file.unlink()