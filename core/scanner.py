# core/scanner.py
"""This module provides functionality to scan a project directory and return Python files with structural information."""

from pathlib import Path
from typing import List
from models.scan_result import FileNode, DirectoryNode, ScanResult

def scan_project(project_path: str, ignore_dirs: List[str] = None) -> List[str]:
    """
    Scan a project directory and return all Python files.
    
    Args:
        project_path: Path to the project root.
        ignore_dirs: Directories to ignore during scanning.

    Returns:
        List of relative path to .py files in the project.
    """    
    result = scan_project_with_tree(project_path, ignore_dirs)
    return result.all_files

def scan_project_with_tree(project_path: str, ignore_dirs: List[str] = None) -> ScanResult:
    """
    Scan project and return detailed structure with tree and metadata.
    
    Args:
        project_path: Path to the project root
        ignore_dirs: Directories to ignore during scanning
        
    Returns:
        ScanResult with tree structure, file list, and metadata
    """
    if ignore_dirs is None:
        ignore_dirs = ["venv", ".venv", "__pycache__", ".git", "node_modules"]
    
    project_path = Path(project_path)

    # Validation
    if not project_path.exists():
        raise FileNotFoundError(f"Path does not exist: {project_path}")
    if not project_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {project_path}")
    
    all_files = []
    entry_points = []
    total_size = 0
    
    def build_tree(dir_path: Path) -> DirectoryNode:
        nonlocal total_size
        
        node = DirectoryNode(
            name=dir_path.name or str(dir_path),
            path=str(dir_path.relative_to(project_path)) if dir_path != project_path else "."
        )
        
        try:
            for item in sorted(dir_path.iterdir()):
                # Skip ignored directories
                if item.is_dir():
                    if item.name in ignore_dirs or item.name.startswith('.'):
                        continue
                    subdir = build_tree(item)
                    if subdir.files or subdir.subdirs:  # Only add non-empty
                        node.subdirs.append(subdir)
                
                # Process Python files
                elif item.is_file() and item.suffix == '.py':
                    relative_path = str(item.relative_to(project_path))
                    size = item.stat().st_size
                    total_size += size
                    
                    # Check if entry point
                    is_entry = _check_entry_point(item)
                    if is_entry:
                        entry_points.append(relative_path)
                    
                    file_node = FileNode(
                        path=relative_path,
                        name=item.name,
                        size_bytes=size,
                        is_entry_point=is_entry
                    )
                    node.files.append(file_node)
                    all_files.append(relative_path)
        
        except PermissionError:
            pass
        
        return node
    
    tree = build_tree(project_path)
    
    return ScanResult(
        project_root=str(project_path),
        tree=tree,
        all_files=all_files,
        entry_points=entry_points,
        total_files=len(all_files),
        total_size_bytes=total_size
    )


def _check_entry_point(file_path: Path) -> bool:
    """Check if file has if __name__ == '__main__'."""
    try:
        content = file_path.read_text(encoding='utf-8')
        return 'if __name__' in content and '__main__' in content
    except:
        return False

            

if __name__ == "__main__":
    project_path = input("Enter the path to the project: ")
    ignore_dirs_input = [
        "venv", ".git", "node_modules", "__pycache__", 
        ".venv", "dist", "build", ".pytest_cache"
    ]

    try:
        # Test flat scan
        python_files = scan_project(project_path, ignore_dirs_input)
        print(f"Found {len(python_files)} Python files:")
        for file in python_files:
            print(f"  {file}")
        
        # Test tree scan
        print(f"\n{'='*50}")
        print("PROJECT STRUCTURE:")
        print(f"{'='*50}\n")
        
        result = scan_project_with_tree(project_path, ignore_dirs_input)
        print(result.get_tree_string())
        
        print(f"\nTotal files: {result.total_files}")
        print(f"Total size: {result.total_size_mb:.2f} MB")
        print(f"Entry points: {result.entry_points}")
    
    except Exception as e:
        print(f"Error scanning project: {e}")