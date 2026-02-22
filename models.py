# models.py
"""This module defines data models for representing parsed information from Python files, including functions, classes, and modules."""
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