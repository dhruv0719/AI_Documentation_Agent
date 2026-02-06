# core/scanner.py
"""
Repository Scanner Module

Responsible for:
- Traversing project directories
- Building file/folder hierarchy
- Identifying relevant source files
- Filtering ignored directories and files
"""

from pathlib import Path
from typing import Generator

from config import ScannerConfig, get_config
from models.schemas import DirectoryNode, ProjectStructure
from utils.file_utils import get_file_size, is_binary_file
from utils.logger import get_logger

logger = get_logger(__name__)

class RepositoryScanner:
    """
    Scans a repository and builds a structured representation
    of its files and directories.
    
    Example:
        scanner = RepositoryScanner("/path/to/project")
        structure = scanner.scan()
        print(structure.root_node.to_tree_string())
    """
    def __init__(
            self,
            root_path: Path,
            config: ScannerConfig | None = None,
    ):
        """
        Initialize the scanner.
        
        Args:
            root_path: Path to the project root directory
            config: Scanner configuration (uses global config if not provided)
        """
        self.root_path = Path(root_path).resolve()
        self.config = config or get_config().scanner
        
        if not self.root_path.exists():
            raise ValueError(f"Path does not exist: {self.root_path}")
        if not self.root_path.is_dir():
            raise ValueError(f"Path is not a directory: {self.root_path}")
        
        logger.info(f"Initialized scanner for: {self.root_path}")

    def scan(self) -> ProjectStructure:
        """
        Perform a complete scan of the repository.
        
        Returns:
            ProjectStructure containing the complete file/folder hierarchy
        """
        logger.info("Starting repository scan...")

        # Build directory tree
        root_node = self._build_directory_tree(self.root_path)
        
        # Collect all relevant files
        all_files = list(self._find_source_files())
        
        # Count totals
        total_dirs = self._count_directories(root_node)

        structure = ProjectStructure(
            root_path=self.root_path,
            root_node=root_node,
            all_files=all_files,
            total_files=len(all_files),
            total_directories=total_dirs
        )

        logger.info(
            f"Scan complete: {structure.total_files} files, "
            f"{structure.total_directories} directories"
        )
        
        return structure

    def _build_directory_tree(self, path: Path) -> DirectoryNode:
        """
        Recursively build a directory tree structure.
        
        Args:
            path: Current directory path
        
        Returns:
            DirectoryNode representing the directory
        """
        node = DirectoryNode(
            name=path.name or str(path),
            path=path,
            children=[],
            files=[]
        )
        try:
            for item in sorted(path.iterdir()):
                # Skip ignored directories/files
                if item.is_dir():
                    if item.name in self.config.ignore_dirs:
                        logger.debug(f"Ignoring directory: {item}")
                        continue
                    if item.name.startswith("."):
                        logger.debug(f"Ignoring hidden directory: {item}")
                        continue

                    child_node = self._build_directory_tree(item)
                    # Only add non-empty directories
                    if child_node.files or child_node.children:
                        node.children.append(child_node)
                
                # Add files that match our criteria
                elif item.is_file():
                    if self._should_inculde_file(item):
                        node.files.append(item.name)

        except Exception as e:
            logger.warning(f"Permission denied: {path}")

        return node
    
    def _find_source_files(self) -> Generator[Path, None, None]:
        """
        Find all relevant source files in the repository.
        
        Yields:
            Path objects for each relevant source file
        """
        for file_path in self.root_path.rglob("*"):
            if file_path.is_file() and self._should_include_file(file_path):
                yield file_path

    def _should_include_file(self, file_path: Path) -> bool:
        """
        Determine if a file should be included in the scan.
        
        Args:
            file_path: Path to the file
        
        Returns:
            True if file should be included
        """
        # Check if in ignored directory
        for parent in file_path.parents:
            if parent.name in self.config.ignore_dirs:
                return False
            if parent.name.startswith(".") and parent != self.root_path:
                return False
        
        # Check extension
        if file_path.suffix not in self.config.include_extensions:
            return False
        
        # Check ignored files
        if file_path.name in self.config.ignore_files:
            return False
        
        # Check file size
        if get_file_size(file_path) > self.config.max_file_size:
            logger.debug(f"Skipping large file: {file_path}")
            return False
        
        # Skip binary files
        if is_binary_file(file_path):
            return False
        
        return True

    def _count_directories(self, node: DirectoryNode) -> int:
        """Count total directories in tree"""
        count = 1 # Count current directory
        for child in node.children:
            count += self._count_directories(child)
        return count
    
    def get_file_tree_string(self, structure: ProjectStructure) -> str:
        """
        Get a string representation of the file tree.
        
        Args:
            structure: ProjectStructure from scan
        
        Returns:
            Tree-formatted string
        """
        return structure.root_node.to_tree_string()