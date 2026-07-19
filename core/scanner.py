# core/scanner.py
"""
This module provides functionality to scan a project directory and return files for
supported languages (Python, JavaScript, TypeScript, and their JSX/TSX variants).

Fixes applied when extending from Python-only to multi-language:
  - FileNode.language was never set (always the "" default), which silently broke
    framework detection in core/frameworks.py since it filters on node.language.
  - The .py and .js branches were separately hardcoded and duplicated; replaced
    with one branch driven by SourceLanguage.from_extension so adding a language
    is a models/language.py change, not a scanner.py change.
  - JS/TS entry-point detection was previously hardcoded to False with a comment
    saying "not checked" - now uses the same lightweight text-search approach
    already used for Python's if __name__ check, looking for
    require.main === module. This mirrors the existing design: the scanner does
    cheap text-based detection for the file tree; the actual parsers
    (python_parser.py / javascript_parser.py / typescript_parser.py) do the
    accurate AST/tree-sitter-based check later when generating docs.
  - detect_frameworks was imported but never called - now wired in and returned
    on ScanResult.frameworks.
  - ScanResult.languages is now populated with the distinct languages found.
"""

import sys
from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.scan_result import FileNode, DirectoryNode, ScanResult
from models.language import SourceLanguage
from core.frameworks import detect_frameworks

DEFAULT_IGNORE_DIRS = [
    "venv", ".venv", "__pycache__", ".git", "node_modules",
    "dist", "build", ".pytest_cache",
]


def scan_project(project_path: str, ignore_dirs: Optional[List[str]] = None,
                  include_extensions: Optional[List[str]] = None) -> List[str]:
    """
    Scan a project directory and return all supported source files
    (Python, JavaScript, TypeScript, JSX, TSX).

    Args:
        project_path: Path to the project root.
        ignore_dirs: Directories to ignore during scanning.

    Returns:
        List of relative paths to supported source files in the project.
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
        ignore_dirs = list(DEFAULT_IGNORE_DIRS)

    project_path = Path(project_path)

    if not project_path.exists():
        raise FileNotFoundError(f"Path does not exist: {project_path}")
    if not project_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {project_path}")

    all_files: List[str] = []
    entry_points: List[str] = []
    languages_seen: set = set()
    total_size = 0

    def build_tree(dir_path: Path) -> DirectoryNode:
        nonlocal total_size

        node = DirectoryNode(
            name=dir_path.name or str(dir_path),
            path=str(dir_path.relative_to(project_path)) if dir_path != project_path else "."
        )

        try:
            for item in sorted(dir_path.iterdir()):
                if item.is_dir():
                    if item.name in ignore_dirs or item.name.startswith('.'):
                        continue
                    subdir = build_tree(item)
                    if subdir.files or subdir.subdirs:
                        node.subdirs.append(subdir)
                    continue

                if not item.is_file():
                    continue

                try:
                    language = SourceLanguage.from_extension(item.suffix)
                except ValueError:
                    # Unsupported extension - not an error, just not a source file
                    # we track (e.g. .json, .md, .png).
                    continue

                relative_path = str(item.relative_to(project_path))
                size = item.stat().st_size
                total_size += size
                languages_seen.add(language.value)

                is_entry = _check_entry_point(item, language)
                if is_entry:
                    entry_points.append(relative_path)

                file_node = FileNode(
                    path=relative_path,
                    name=item.name,
                    size_bytes=size,
                    is_entry_point=is_entry,
                    language=language.value,
                )
                node.files.append(file_node)
                all_files.append(relative_path)

        except PermissionError:
            pass

        return node

    tree = build_tree(project_path)

    # Flatten all FileNodes for framework detection (tree only stores files
    # per-directory, so we need one pass to collect every node).
    all_file_nodes: List[FileNode] = []

    def _collect(dir_node: DirectoryNode):
        all_file_nodes.extend(dir_node.files)
        for sub in dir_node.subdirs:
            _collect(sub)

    _collect(tree)

    frameworks = detect_frameworks(project_path, all_file_nodes)

    return ScanResult(
        project_root=str(project_path),
        tree=tree,
        all_files=all_files,
        entry_points=entry_points,
        total_files=len(all_files),
        total_size_bytes=total_size,
        languages=sorted(languages_seen),
        frameworks=frameworks,
    )


def _check_entry_point(file_path: Path, language: SourceLanguage) -> bool:
    """Lightweight text-based entry-point check, per language.

    This is intentionally cheap (string search, not AST/tree-sitter parsing) -
    it's meant for fast project-tree scanning, not authoritative detection.
    The real parsers do the accurate check later when generating docs.
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return False

    if language == SourceLanguage.PYTHON:
        return 'if __name__' in content and '__main__' in content
    if language in (SourceLanguage.JAVASCRIPT, SourceLanguage.TYPESCRIPT):
        return 'require.main' in content and 'module' in content

    return False


if __name__ == "__main__":
    project_path = input("Enter the path to the project: ")

    try:
        source_files = scan_project(project_path)
        print(f"Found {len(source_files)} source files:")
        for file in source_files:
            print(f"  {file}")

        print(f"\n{'='*50}")
        print("PROJECT STRUCTURE:")
        print(f"{'='*50}\n")

        result = scan_project_with_tree(project_path)
        print(result.get_tree_string())

        print(f"\nTotal files: {result.total_files}")
        print(f"Total size: {result.total_size_mb:.2f} MB")
        print(f"Languages: {result.languages}")
        print(f"Frameworks: {result.frameworks}")
        print(f"Entry points: {result.entry_points}")

    except Exception as e:
        print(f"Error scanning project: {e}")