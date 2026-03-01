# models/change_report.py
"""This module defines the ChangeReport data model, which captures the differences between the current state of a project and its previous analysis. It identifies added, modified, deleted, and unchanged files to determine what needs to be re-analyzed."""

from dataclasses import dataclass
from typing import List

@dataclass
class ChangeReport:
    """Report of what changed since last analysis."""
    added_files: List[str] # New File
    modified_files: List[str] # Existing file with changes
    deleted_files: List[str] # Files that were removed
    unchanged_files: List[str] # Files that are the same as last time

    @property
    def has_changes(self) -> bool:
        """Check if there are any changes."""
        return bool(self.added_files or self.modified_files or self.deleted_files)
    
    @property
    def files_to_analyze(self) -> List[str]:
        """List of files that need analysis (added or modified)."""
        return self.added_files + self.modified_files
    
    def summary(self) -> str:
        """Human-readable summary of changes"""
        return f"""
Change Detection Summary:
- Added: {len(self.added_files)} files
- Modified: {len(self.modified_files)} files
- Deleted: {len(self.deleted_files)} files
- Unchanged: {len(self.unchanged_files)} files

Files to Analyze: {len(self.files_to_analyze)} (Added + Modified)
"""