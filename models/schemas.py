# models/schemas.py
"""
Data Models and Schemas for Code Documentation Agent

Defines all data structures used throughout the application:
- Parsed code elements (functions, classes, modules)
- Documentation structures
- Analysis results
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class CodeElementType(str, Enum):
    """Types of code elements that can be parsed"""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    ASYNC_FUNCTION = "async_function"
    VARIABLE = "variable"
    IMPORT = "import"


class Parameter(BaseModel):
    """Function/Method parameter"""
    name: str
    type_hint: Optional[str] = None
    default_value: Optional[str] = None
    
    def __str__(self) -> str:
        result = self.name
        if self.type_hint:
            result += f": {self.type_hint}"
        if self.default_value:
            result += f" = {self.default_value}"
        return result


class FunctionInfo(BaseModel):
    """Information about a function or method"""
    name: str
    element_type: CodeElementType = CodeElementType.FUNCTION
    parameters: list[Parameter] = Field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    decorators: list[str] = Field(default_factory=list)
    line_number: int = 0
    end_line_number: int = 0
    is_async: bool = False
    is_private: bool = False
    source_code: Optional[str] = None
    
    @property
    def signature(self) -> str:
        """Generate function signature string"""
        params = ", ".join(str(p) for p in self.parameters)
        prefix = "async " if self.is_async else ""
        return_str = f" -> {self.return_type}" if self.return_type else ""
        return f"{prefix}def {self.name}({params}){return_str}"


class ClassInfo(BaseModel):
    """Information about a class"""
    name: str
    element_type: CodeElementType = CodeElementType.CLASS
    bases: list[str] = Field(default_factory=list)
    docstring: Optional[str] = None
    decorators: list[str] = Field(default_factory=list)
    methods: list[FunctionInfo] = Field(default_factory=list)
    class_variables: list[str] = Field(default_factory=list)
    line_number: int = 0
    end_line_number: int = 0
    is_dataclass: bool = False
    
    @property
    def public_methods(self) -> list[FunctionInfo]:
        """Get only public methods"""
        return [m for m in self.methods if not m.is_private]


class ImportInfo(BaseModel):
    """Information about an import statement"""
    module: str
    names: list[str] = Field(default_factory=list)
    is_from_import: bool = False
    alias: Optional[str] = None


class ModuleInfo(BaseModel):
    """Information about a Python module (file)"""
    file_path: Path
    relative_path: str
    module_name: str
    docstring: Optional[str] = None
    imports: list[ImportInfo] = Field(default_factory=list)
    classes: list[ClassInfo] = Field(default_factory=list)
    functions: list[FunctionInfo] = Field(default_factory=list)
    global_variables: list[str] = Field(default_factory=list)
    line_count: int = 0
    
    @property
    def has_content(self) -> bool:
        """Check if module has meaningful content"""
        return bool(self.classes or self.functions)


class DirectoryNode(BaseModel):
    """Represents a directory in the project structure"""
    name: str
    path: Path
    children: list["DirectoryNode"] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)
    
    def to_tree_string(self, prefix: str = "", is_last: bool = True) -> str:
        """Generate tree-style string representation"""
        connector = "└── " if is_last else "├── "
        result = f"{prefix}{connector}{self.name}/\n"
        
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        # Add files
        for i, file in enumerate(self.files):
            file_connector = "└── " if (i == len(self.files) - 1 and not self.children) else "├── "
            result += f"{new_prefix}{file_connector}{file}\n"
        
        # Add subdirectories
        for i, child in enumerate(self.children):
            result += child.to_tree_string(new_prefix, i == len(self.children) - 1)
        
        return result


class ProjectStructure(BaseModel):
    """Complete project structure information"""
    root_path: Path
    root_node: DirectoryNode
    all_files: list[Path] = Field(default_factory=list)
    total_files: int = 0
    total_directories: int = 0


class ModuleAnalysis(BaseModel):
    """LLM analysis result for a module"""
    module_path: str
    purpose: str
    responsibilities: list[str] = Field(default_factory=list)
    key_components: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    complexity_notes: Optional[str] = None


class ProjectAnalysis(BaseModel):
    """Complete project analysis result"""
    project_name: str
    project_purpose: str
    architecture_overview: str
    key_modules: list[ModuleAnalysis] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    entry_points: list[str] = Field(default_factory=list)
    design_patterns: list[str] = Field(default_factory=list)


class DocumentationResult(BaseModel):
    """Generated documentation output"""
    overview_doc: str
    technical_doc: str
    generated_at: datetime = Field(default_factory=datetime.now)
    project_path: Path
    files_analyzed: int = 0
    generation_time_seconds: float = 0.0


# Allow forward references
DirectoryNode.model_rebuild()