# parsers/base_parser.py
"""Base parser interface for language-agnostic parsing."""

from abc import ABC, abstractmethod
from typing import List, Optional
from models.parsed_file import ParsedFile

class BaseParser(ABC):
    """
    Abstract base class for all language parsers.
    
    Each language (Python, JavaScript, etc.) implements this interface.
    This allows the ParserFactory to work with any language uniformly.
    """
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = project_root
    
    @abstractmethod
    def parse_file(self, file_path: str) -> Optional[ParsedFile]:
        """
        Parse a single file and extract structured information.
        
        Args:
            file_path: Path to file (relative to project_root)
        
        Returns:
            ParsedFile with extracted information, or None if failed
        """
        pass
    
    @abstractmethod
    def parse_files(self, file_paths: List[str]) -> List[ParsedFile]:
        """Parse multiple files."""
        pass
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Return list of file extensions this parser handles."""
        pass