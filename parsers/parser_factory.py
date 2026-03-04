# parsers/python_factory.py
"""Factory for creating appropriate parser based on file type."""

from pathlib import Path
from typing import Optional, Dict, Type
from parsers.base_parser import BaseParser
from parsers.python_parser import PythonParser

class ParserFactory:
    """
    Factory to get the right parser for each file type.
    
    Usage:
        factory = ParserFactory(project_root="/path/to/project")
        parser = factory.get_parser("main.py")
        parsed = parser.parse_file("main.py")
    """

    # Registry of parsers by extension
    _parsers: Dict[str, Type[BaseParser]] = {
        '.py': PythonParser,
        # Future:
        # '.js': JavaScriptParser,
        # '.ts': TypeScriptParser,
    }

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = project_root
        self._parser_instances: Dict[str, BaseParser] = {}
    
    def get_parser(self, file_path: str) -> Optional[BaseParser]:
        """
        Get appropriate parser for a file.
        
        Args:
            file_path: Path to the file
        
        Returns:
            Parser instance or None if unsupported
        """
        ext = Path(file_path).suffix.lower()
        
        if ext not in self._parsers:
            return None
        
        # Cache parser instances
        if ext not in self._parser_instances:
            parser_class = self._parsers[ext]
            self._parser_instances[ext] = parser_class(self.project_root)
        
        return self._parser_instances[ext]
    
    def can_parse(self, file_path: str) -> bool:
        """Check if we have a parser for this file type."""
        ext = Path(file_path).suffix.lower()
        return ext in self._parsers
    
    @classmethod
    def register_parser(cls, extension: str, parser_class: Type[BaseParser]):
        """Register a new parser for an extension."""
        cls._parsers[extension] = parser_class
    
    @property
    def supported_extensions(self) -> list:
        """List all supported extensions."""
        return list(self._parsers.keys())