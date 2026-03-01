# models/metadata.py
"""This module defines data models for representing metadata about files and projects, including file hashes, last analysis timestamps, and summaries of file contents. This metadata is crucial for change detection and efficient re-analysis of only modified files."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict
from models.parsed_file import ModuleSummary

@dataclass
class FileMetadata:
    """Metadata about a single file."""
    file_path: str
    hash: str # SHA-256 hash of the file content
    last_analyzed: datetime
    size_bytes: int
    summary: Optional[ModuleSummary] = None  # Short summary of the file's purpose

@dataclass
class ProjectMetadata:
    """Metadata for entire project."""
    project_name: str
    project_root: str
    last_updated: datetime
    files: Dict[str, FileMetadata]  # file_path → metadata

    def to_json(self) -> Dict:
        """Serialize to JSON for storage."""
        return {
            "project_name": self.project_name,
            "project_root": self.project_root,
            "last_updated": self.last_updated.isoformat(),
            "files": {fp: {
                "file_path": fm.file_path,
                "hash": fm.hash,
                "last_analyzed": fm.last_analyzed.isoformat(),
                "size_bytes": fm.size_bytes,
                "summary": fm.summary.to_dict() if fm.summary else None
            } for fp, fm in self.files.items()}
        }
    
    @staticmethod
    def from_json(data: Dict) -> 'ProjectMetadata':
        """Deserialize from JSON."""
        return ProjectMetadata(
            project_name=data["project_name"],
            project_root=data["project_root"],
            last_updated=datetime.fromisoformat(data["last_updated"]),
            files={fp: FileMetadata(
                file_path=fm["file_path"],
                hash=fm["hash"],
                last_analyzed=datetime.fromisoformat(fm["last_analyzed"]),
                size_bytes=fm["size_bytes"],
                summary=ModuleSummary.from_dict(fm["summary"]) if fm["summary"] else None
            ) for fp, fm in data["files"].items()}
        )