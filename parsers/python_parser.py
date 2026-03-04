# parser/python_parser.py
"""This module provides functionality to parse Python files and extract structured information about classes, functions, imports, and docstrings."""

import ast
from pathlib import Path
from typing import Optional, List
from core.scanner import scan_project
from models.parsed_file import ParsedFile, ClassInfo, FunctionInfo, ParameterInfo, ImportInfo

class PythonParser:
    """
    Enhanced Python parser using AST.
    
    Extracts:
    - Classes with base classes, decorators, methods
    - Functions with parameters, types, decorators
    - Structured imports
    - Global variables
    - Entry point detection
    """
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else None

    def parse_file(self, file_path: str) -> Optional[ParsedFile]:
        """Parse a Python file and extract all information."""

        # Resolve full path
        if self.project_root: 
            full_path = self.project_root / file_path
        else: 
            full_path = Path(file_path)

        try: 
            content = full_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(full_path))
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return None
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
        
        # Extract all components
        parsed = ParsedFile(
            file_path=file_path,
            module_docstring=ast.get_docstring(tree),
            imports=self._extract_imports(tree),
            classes=self._extract_classes(tree),
            functions=self._extract_functions(tree),
            global_variables=self._extract_global_variables(tree),
            line_count=len(content.splitlines()),
            has_entry_point=self._check_entry_point(tree)
        )
        
        return parsed
    
    def parse_files(self, file_paths: List[str]) -> List[ParsedFile]:
        """Parse multiple files, skip failures."""
        results = []
        for fp in file_paths:
            parsed = self.parse_file(fp)
            if parsed and parsed.has_content:
                results.append[parsed]
        return results
    
    def _extract_imports(self, tree: ast.Module) -> List[ImportInfo]:
        """Extract all imports with full details."""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(ImportInfo(
                        module=alias.name,
                        alias=alias.asname,
                        is_from_import=False
                    ))
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(ImportInfo(
                        module=node.module,
                        names=[alias.name for alias in node.names],
                        is_from_import=True
                    ))

        return imports
    
    def _extract_classes(self, tree: ast.Module) -> List[ClassInfo]:
        """Extract all class definitions."""
        classes = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(self._parse_class(node))

        return classes
    
    def _parse_class(self, node: ast.ClassDef) -> ClassInfo:
        """Parse a single class definition."""

        # Extract base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(self._get_attribute_name(base))

        # Extract decorators
        decorators = self._extract_decorators(node)

        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = self._parse_function(item)
                method.is_method = True
                methods.append(method)

        # Extract class variables
        class_variables = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                class_variables.append(item.target.id)
            elif isinstance(item, ast.AnnAssign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_variables.append(target.id)

        return ClassInfo(
            name=node.name,
            docstring=ast.get_docstring(node),
            methods=methods,
            base_classes=base_classes,
            decorators=decorators,
            class_variables=class_variables,
            line_number=node.lineno
        )
    
    def _extract_functions(self, tree: ast.Module) -> List[FunctionInfo]:
        """Extract top-level functions only."""
        functions = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(self._parse_function(node))

        return functions
    
    def _parse_function(self, node) -> FunctionInfo:
        """Parse a function or method definition."""

        # Determine if async
        is_async = isinstance(node, ast.AsyncFunctionDef)

        # Extract parameters with details
        params = self._extract_parameters(node.args)

        # Extract return type
        returns = None
        if node.returns:
            returns = self._annotation_to_string(node.returns)

        # Extract decorators
        decorators = self._extract_decorators(node)
        
        return FunctionInfo(
            name=node.name,
            params=params,
            returns=returns,
            docstring=ast.get_docstring(node),
            decorators=decorators,
            is_async=is_async,
            is_private=node.name.startswith('_'),
            line_number=node.lineno
        )
    
    def _extract_parameters(self, args: ast.arguments) -> List[ParameterInfo]:
        """Extract function parameters with types and defaults."""
        params = []

        # Calculate where defaults start
        num_args= len(args.args)
        num_defaults = len(args.defaults)
        first_default_idx = num_args - num_defaults

        for i, arg in enumerate(args.args):
            # Get type hint
            type_hint = None
            if arg.annotation:
                type_hint = self._annotation_to_string(arg.annotation)

            # Get default value
            default_value = None
            default_idx = i - first_default_idx
            if default_idx >= 0 and default_idx < len(args.defaults):
                default_value = self._node_to_string(args.defaults[default_idx])

            params.append(ParameterInfo(
                name=arg.arg,
                type_hint=type_hint,
                default_value=default_value
            ))

        # Handle *args
        if args.vararg:
            params.append(ParameterInfo(
                name=f"*{args.vararg.arg}",
                type_hint=self._annotation_to_string(args.vararg.annotation) if args.vararg.annotation else None
            ))

        # Handle **kwargs
        if args.kwarg:
            params.append(ParameterInfo(
                name=f"**{args.kwarg.arg}",
                type_hint=self._annotation_to_string(args.kwarg.annotation) if args.kwarg.annotation else None
            ))

        return params
    
    def _extract_decorators(self, node) -> List[str]:
        """Extract decorator names from a function or class."""
        decorators = []

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    decorators.append(decorator.func.id)
                elif isinstance(decorator.func, ast.Attribute):
                    decorators.append(self._get_attribute_name(decorator.func))
            elif isinstance(decorator, ast.Attribute):
                decorators.append(self._get_attribute_name(decorator))
        
        return decorators
    
    def _extract_global_variables(self, tree: ast.Module) -> List[str]:
        """Extract module-level variable assignments."""
        variables = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Skip dunder variables
                        if not target.id.startswith('__'):
                            variables.append(target.id)
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    variables.append(node.target.id)
        
        return variables
    
    def _check_entry_point(self, tree: ast.Module) -> bool:
        """Check if module has if __name__ == '__main__'."""
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Check for __name__ == "__main__"
                test = node.test
                if isinstance(test, ast.Compare):
                    if isinstance(test.left, ast.Name) and test.left.id == '__name__':
                        return True
        return False
    
    def _annotation_to_string(self, node) -> str:
        """Convert type annotation to string."""
        if node is None:
            return None
        
        try:
            return ast.unparse(node)
        except:
            # Fallback for older Python versions
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Constant):
                return repr(node.value)
            return str(node)
        
    def _node_to_string(self, node) -> str:
        """Convert AST node to string representation."""
        try:
            return ast.unparse(node)
        except:
            if isinstance(node, ast.Constant):
                return repr(node.value)
            elif isinstance(node, ast.Name):
                return node.id
            return "..."
        
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get full attribute name like 'module.Class'."""
        parts = []
        current = node
        
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        
        if isinstance(current, ast.Name):
            parts.append(current.id)
        
        return ".".join(reversed(parts))


# Backward compatible function
def parse_file(file_path: str, project_root: Optional[str] = None) -> Optional[ParsedFile]:
    """Parse a single file (backward compatible)."""
    parser = PythonParser(project_root)
    return parser.parse_file(file_path)

if __name__ == "__main__":
    # Test the enhanced parser
    parser = PythonParser(r'D:\AI_Documentation_Agent')
    
    from core.scanner import scan_project
    files = scan_project(r'D:\AI_Documentation_Agent', ignore_dirs=["venv", ".venv", "__pycache__"])
    
    print(f"Found {len(files)} files\n")
    
    for f in files:  # Test first 3 files
        parsed = parser.parse_file(f)
        if parsed:
            print(f"=" * 50)
            print(f"File: {parsed.file_path}")
            print(f"Lines: {parsed.line_count}")
            print(f"Entry Point: {parsed.has_entry_point}")
            print(f"\nImports ({len(parsed.imports)}):")
            for imp in parsed.imports[:5]:
                print(f"  - {imp}")
            print(f"\nClasses ({len(parsed.classes)}):")
            for cls in parsed.classes:
                print(f"  - {cls.name}")
                print(f"    Bases: {cls.base_classes}")
                print(f"    Decorators: {cls.decorators}")
                print(f"    Methods: {[m.name for m in cls.methods]}")
            print(f"\nFunctions ({len(parsed.functions)}):")
            for func in parsed.functions:
                print(f"  - {func.signature}")
                print(f"    Decorators: {func.decorators}")
            print()