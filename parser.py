import ast
from pathlib import Path
from typing import Optional
from models import ParsedFile, ClassInfo, FunctionInfo

def parse_file(file_path: str, project_root: Optional[str] = None) -> ParsedFile:
    """Parse a Python file and extract structured information."""
    pass

full_path = input('Enter the path to the Python file to parse: ')

# Parse file
with open(full_path, 'r', encoding='utf-8') as file:
    tree = ast.parse(file.read(), filename=full_path)

# Get module docstring
module_docstring = ast.get_docstring(tree)

# Iterate top-level nodes
for node in tree.body:
    if isinstance(node, ast.ClassDef):
        # Extract class information
        class_name = node.name
        class_doc = ast.get_docstring(node)
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                function_info = FunctionInfo(
                    name=item.name,
                    docstring=ast.get_docstring(item),
                    params=[arg.arg for arg in item.args.args]
                )
                methods.append(function_info)

    elif isinstance(node, ast.FunctionDef):
        # Extract function information
        function_info = FunctionInfo(
            name=node.name,
            docstring=ast.get_docstring(node),
            params=[arg.arg for arg in node.args.args],
            returns = ast.unparse(node.returns) if node.returns else None 
        )

    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        imports = []
        import_name = node.module
        if import_name:
            imports.append(import_name)