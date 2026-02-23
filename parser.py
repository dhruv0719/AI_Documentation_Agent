# parser.py
"""This module provides functionality to parse Python files and extract structured information about classes, functions, imports, and docstrings."""
import ast
from pathlib import Path
from typing import Optional
from scanner import scan_project
from models import ParsedFile, ClassInfo, FunctionInfo

def parse_file(file_path: str, project_root: Optional[str] = None) -> Optional[ParsedFile]:
    """Parse a Python file and extract structured information."""
    
    # Initialize data structures
    imports = []
    classes = []
    functions = []

    # Build full 
    if project_root is None:
        full_path = Path(file_path)
    else:
        full_path = Path(project_root) / file_path

    try:
        # Read and parse
        with open(full_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=full_path)
        
        # Extract module docstring
        module_docstring = ast.get_docstring(tree)

        # Process each top-level node
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                # Extract class
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = _extract_function_info(item)
                        methods.append(method_info)

                class_info = ClassInfo(
                    name=node.name,
                    docstring=ast.get_docstring(node),
                    methods=methods
                )
                classes.append(class_info)

            elif isinstance(node, ast.FunctionDef):
                func_info = _extract_function_info(node)
                functions.append(func_info) 

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return ParsedFile(
            file_path=file_path,
            module_docstring=module_docstring,
            imports=imports,
            classes=classes,
            functions=functions
        )
    
    except Exception as e:
        print(f"Warning: Skipping {file_path} due to parsing error: {e}")
        return None

def _extract_function_info(node: ast.FunctionDef) -> FunctionInfo:
    """Helper to extract function/method information."""
    params =[]
    for arg in node.args.args:
        if arg.annotation:
            param_str = f"{arg.arg}: {ast.unparse(arg.annotation)}"
        else:
            param_str = arg.arg
        params.append(param_str)

    returns = ast.unparse(node.returns) if node.returns else None

    return FunctionInfo(
        name=node.name,
        docstring=ast.get_docstring(node),
        params=params,
        returns=returns
    )

if __name__ == "__main__":
    project_root = r'D:\AI_Documentation_Agent'
    files = scan_project(project_root, ignore_dirs=["venv", ".venv", "__pycache__"])
    
    print(f"Found {len(files)} files. Parsing first one...\n")
    
    if files:
        parsed = parse_file(files[0], project_root)
        if parsed:
            print(f"File: {parsed.file_path}")
            print(f"Imports: {parsed.imports}")
            print(f"Classes: {[c.name for c in parsed.classes]}")
            print(f"Functions: {[f.name for f in parsed.functions]}")
