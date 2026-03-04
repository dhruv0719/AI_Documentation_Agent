# models/scan_result.py
"""Data models for project scanning results, including file trees, directory structures, and scan metadata."""

from dataclasses import dataclass, field
from typing import List

@dataclass
class FileNode:
    """Represents a file in the project."""
    path: str           # Relative path from project root
    name: str           # Just the filename
    size_bytes: int     # File size
    is_entry_point: bool = False  # Has if __name__ == "__main__"

@dataclass
class DirectoryNode:
    """Represents a directory in the project structure."""
    name: str
    path: str
    files: List[FileNode] = field(default_factory=list)
    subdirs: List['DirectoryNode'] = field(default_factory=list)

    def to_tree_string(self, prefix: str = "", is_last: bool = True) -> str:
        """Generate ASCII tree representation."""
        connector = "└── " if is_last else "├── "
        result = f"{prefix}{connector}{self.name}/\n"
        
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        # Add files
        for i, file in enumerate(self.files):
            is_last_item = (i == len(self.files) - 1) and not self.subdirs
            file_connector = "└── " if is_last_item else "├── "
            result += f"{new_prefix}{file_connector}{file.name}\n"
        
        # Add subdirectories
        for i, subdir in enumerate(self.subdirs):
            result += subdir.to_tree_string(new_prefix, i == len(self.subdirs) - 1)
        
        return result
    
@dataclass
class ScanResult:
    """Complete scan result with tree structure and metadata."""
    project_root: str                # Absolute path to project
    tree: DirectoryNode              # Hierarchical tree structure
    all_files: List[str]             # Flat list of all file paths
    entry_points: List[str]          # Files with if __name__ == "__main__"
    total_files: int                 # Total Python files found
    total_size_bytes: int            # Total size of all Python files
    
    @property
    def total_size_mb(self) -> float:
        """Total size in megabytes."""
        return self.total_size_bytes / (1024 * 1024)
    
    def get_tree_string(self) -> str:
        """Get ASCII tree representation of project structure."""
        # Start with root name, then children
        result = f"{self.tree.name}/\n"
        
        # Add files at root level
        total_items = len(self.tree.files) + len(self.tree.subdirs)
        item_index = 0
        
        for i, file in enumerate(self.tree.files):
            item_index += 1
            is_last = item_index == total_items
            connector = "└── " if is_last else "├── "
            result += f"{connector}{file.name}\n"
        
        for i, subdir in enumerate(self.tree.subdirs):
            item_index += 1
            is_last = item_index == total_items
            result += subdir.to_tree_string(prefix="", is_last=is_last)
        
        return result
