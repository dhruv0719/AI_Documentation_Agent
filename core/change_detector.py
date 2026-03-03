# core/change_detector.py

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from core.hasher import FileHasher
from core.metadata_store import MetadataStore
from models.metadata import ProjectMetadata, FileMetadata
from models.change_report import ChangeReport
from models.parsed_file import ModuleSummary

class ChangeDetector:
    """Detects which files changed since last analysis."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.store = MetadataStore(project_root)
        self.hasher = FileHasher()

        # Load metadata Once from disk
        self._metadata : Optional[ProjectMetadata] = self.store.load()

        # Cache hashes computed during detect_changes(), so update_metadata() doesn't re-hash everything
        self._current_hashes : Dict[str, str] = {}

    def detect_changes(self, current_files: List[str]) -> ChangeReport:
        """
        Compare current files against last analysis

        Args:
            current_files: List of file paths from scanner
            
        Returns:
            ChangeReport with categorized changes
        """
        # First run - no previous metadata exists
        if self._metadata is None:
            # Still hash files now so update_metadata() can reuse them
            self._current_hashes = self.hasher.hash_files(current_files)
            return ChangeReport(
                added_files=current_files,
                modified_files=[],
                deleted_files=[],
                unchanged_files=[]
            )
        
        # Hash current files and CACHE for later reuse
        self._current_hashes = self.hasher.hash_files(current_files)
        old_hashes = {f: m.hash for f, m in self._metadata.files.items()}

        # Categorize changes
        current_set = set(current_files)
        old_set = set(old_hashes.keys())

        added = list(current_set - old_set)
        deleted = list(old_set - current_set)

        # Check for modifications in existing files
        modified = []
        unchanged = []

        for file in current_set & old_set:
            if self._current_hashes[file] != old_hashes[file]:
                modified.append(file)
            else:
                unchanged.append(file)

        return ChangeReport(
            added_files=sorted(added),
            modified_files=sorted(modified),
            deleted_files=sorted(deleted),
            unchanged_files=sorted(unchanged)
        )
    
    def get_cached_summary(self, file_path: str) -> Optional[ModuleSummary]:
        """
        Get cached analysis for unchanged file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Cached ModuleSummary or None
        """
        # Pure memory lookup — called in a LOOP for every unchanged file
        if not self._metadata:
            return None

        file_meta = self._metadata.files.get(file_path)
        return file_meta.summary if file_meta else None
    
    def update_metadata(self, analyzed_files: List[str], summaries: Dict[str, ModuleSummary], project_name: str):
        """
        Update metadata after analysis.
        
        Args:
            analyzed_files: Files that were analyzed
            summaries: Map of file_path → ModuleSummary
            project_name: Name of project
        """
        # Reuse cached metadata or create fresh
        if self._metadata is None:
            self._metadata = ProjectMetadata(
                project_name=project_name,
                project_root=str(self.project_root),
                last_updated=datetime.now(),
                files={}
            )
        
        # Reuse cached hashes if available, otherwise compute
        if self._current_hashes:
            hashes = self._current_hashes
        else:
            # Fallback: force mode skips detect_changes, 
            # so hashes might not be cached
            hashes = self.hasher.hash_files(analyzed_files)

        # Update file metadata
        for file_path in analyzed_files:
            file_size = Path(self.project_root / file_path).stat().st_size

            self._metadata.files[file_path] = FileMetadata(
                file_path=file_path,
                hash=hashes.get(file_path, self.hasher.hash_file(
                    str(self.project_root / file_path)
                )),
                last_analyzed=datetime.now(),
                size_bytes=file_size,
                summary=summaries.get(file_path)
            )

        # Remove deleted files
        current_files = set(analyzed_files)
        self._metadata.files = {
            f: m for f, m in self._metadata.files.items() 
            if f in current_files
        }
        # Update timestamp
        self._metadata.last_updated = datetime.now()
        
        # Save to disk
        self.store.save(self._metadata)

    def reload_metadata(self):
        """Force re-read from disk (if external process modified it)."""
        self._metadata = self.store.load()
        self._current_hashes = {}
