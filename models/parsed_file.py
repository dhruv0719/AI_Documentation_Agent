# models/parsed_file.py
"""This module defines data models for representing parsed information from Python files, including functions, classes, and modules. It also includes models for summarizing module and project-level insights after analysis."""
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class FunctionInfo:
    name: str
    params: List[str]
    returns: Optional[str]
    docstring: Optional[str]

@dataclass
class ClassInfo:
    name: str
    docstring: Optional[str]
    methods: List[FunctionInfo]

@dataclass
class ParsedFile:
    file_path: str
    module_docstring: Optional[str]
    imports: List[str]
    classes: List[ClassInfo]
    functions: List[FunctionInfo]

@dataclass
class ModuleSummary:
    """Summary of a single module after LLM analysis."""
    file_path: str
    purpose: str  # What does this module do?
    responsibilities: List[str]  # Main responsibilities
    key_components: List[str]  # Important classes/functions
    dependencies: List[str]  # What it imports (from ParsedFile)

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization"""
        return {
            "file_path": self.file_path,
            "purpose": self.purpose,
            "responsibilities": self.responsibilities,
            "key_components": self.key_components,
            "dependencies": self.dependencies
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'ModuleSummary':
        """Create ModuleSummary from dict"""
        return ModuleSummary(
            file_path=data["file_path"],
            purpose=data["purpose"],
            responsibilities=data["responsibilities"],
            key_components=data["key_components"],
            dependencies=data["dependencies"]
        )

@dataclass 
class ProjectAnalysis:
    """High-level project understanding after synthesis."""
    project_purpose: str
    architecture_overview: str
    entry_points: List[str]
    module_relationships: str  # How modules connect
    design_patterns: List[str]