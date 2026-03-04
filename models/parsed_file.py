# models/parsed_file.py
"""This module defines data models for representing parsed information from Python files, including functions, classes, and modules. It also includes models for summarizing module and project-level insights after analysis."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class ParameterInfo:
    """Detailed parameter information."""
    name: str
    type_hint: Optional[str] = None
    default_value: Optional[str] = None
    
    def __str__(self) -> str:
        """Format: name: type = default"""
        result = self.name
        if self.type_hint:
            result += f": {self.type_hint}"
        if self.default_value:
            result += f" = {self.default_value}"
        return result

@dataclass
class FunctionInfo:
    """Information about a function or method."""
    name: str
    params: List[ParameterInfo]
    returns: Optional[str] = None
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    is_async: bool = False
    is_private: bool = False  # starts with _
    line_number: int = 0

    @property
    def signature(self) -> str:
        """Generate readable signature."""
        params_str = ", ".join(str(p) for p in self.params)
        prefix = "async " if self.is_async else ""
        returns_str = f" -> {self.returns}" if self.returns else ""
        return f"{prefix}def {self.name}({params_str}){returns_str}"

@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    docstring: Optional[str] = None
    methods: List[FunctionInfo] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)  # NEW
    decorators: List[str] = field(default_factory=list)    # NEW
    class_variables: List[str] = field(default_factory=list)  # NEW
    line_number: int = 0

    @property
    def is_dataclass(self) -> bool:
        return "dataclass" in self.decorators
    
@dataclass
class ImportInfo:
    """Structured import information."""
    module: str
    names: List[str] = field(default_factory=list)  # for "from x import a, b"
    alias: Optional[str] = None  # for "import x as y"
    is_from_import: bool = False

    def __str__(self) -> str:
        if self.is_from_import:
            names = ", ".join(self.names)
            return f"from {self.module} import {names}"
        elif self.alias:
            return f"import {self.module} as {self.alias}"
        return f"import {self.module}"

@dataclass
class ParsedFile:
    """Complete parsed information about a Python file."""
    file_path: str
    module_docstring: Optional[str] = None
    imports: List[ImportInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    global_variables: List[str] = field(default_factory=list)
    line_count: int = 0

    @property
    def has_content(self) -> bool:
        """Check if file has meaningful content to document."""
        return bool(self.classes or self.functions)
    
    @property
    def module_name(self) -> str:
        """Extract module name from file path."""
        import os
        return os.path.splitext(os.path.basename(self.file_path))[0]

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