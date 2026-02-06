# core/parser.py
"""
Code Parser Module

Responsible for:
- Parsing Python files using AST
- Extracting classes, functions, and their metadata
- Building structured representations of code elements
"""

import ast
from pathlib import Path
from typing import list, Optional

from models.schemas import (
    ClassInfo,
    CodeElementType,
    FunctionInfo,
    ImportInfo,
    ModuleInfo,
    Parameter,
)
from utils.file_utils import read_file_content, count_lines, get_relative_path
from utils.logger import get_logger

logger = get_logger(__name__)

class CodeParser:
    """
    Parses Python source files and extracts structured information
    about classes, functions, imports, and documentation.
    
    Example:
        parser = CodeParser()
        module_info = parser.parse_file(Path("example.py"))
        for cls in module_info.classes:
            print(f"Class: {cls.name}")
    """
    def __init__(self, base_path: Path):
        """
        Initialize the parser.
        
        Args:
            base_path: Base path for computing relative paths
        """
        self.base_path = base_path

    def parse_file(self, file_path: Path) -> Optional[ModuleInfo]:
        """"
        Parse a Python file and extract its structure.
        
        Args:
            file_path: Path to the Python file
        
        Returns:
            ModuleInfo containing parsed information, or None if parsing fails
        """
        content = read_file_content(file_path)
        if content is None:
            return None
        
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return None

        # Compute relative path and module name
        if self.base_path:
            relative_path = get_relative_path(file_path, self.base_path)
        else:
            relative_path = str(file_path)
        
        module_name = file_path.stem

        # Extract module docstring
        module_docstring = ast.get_docstring(tree)

        # Parse all elements
        imports = self._extract_imports(tree)
        classes = self._extract_classes(tree, content)
        functions = self._extract_functions(tree, content, top_level_only=True)
        global_vars = self._extract_global_variables(tree)

        module_info = ModuleInfo(
            file_path=file_path,
            relative_path=relative_path,
            module_name=module_name,
            docstring=module_docstring,
            imports=imports,
            classes=classes,
            functions=functions,
            global_variables=global_vars,
            line_count=count_lines(content)
        )

        logger.debug(
            f"Parsed {file_path}:"
            f"{len(classes)} classes, {len(functions)} functions"
        )

        return module_info
    
    def parse_files(self, file_paths: list[Path]) -> list[ModuleInfo]:
        """
        Parse multiple files.
        
        Args:
            file_paths: List of file paths to parse
        
        Returns:
            List of successfully parsed ModuleInfo objects
        """
        modules = []
        for file_path in file_paths:
            module_info = self.parse_file(file_path)
            if module_info and module_info.has_content:
                modules.append(module_info)

        logger.info(f"Successfully parsed {len(modules)}/{len(file_paths)} files.")
        return modules
    
    def _extract_imports(self, tree: ast.AST) -> list[ImportInfo]:
        """Extract all import statements from the AST"""
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
                module = node.module or ""
                names = [alias.name for alias in node.names]
                imports.append(ImportInfo(
                    module=module,
                    names=names,
                    is_from_import=True
                ))

        return imports
    
    def _extract_classes(self, tree: ast.Module, source_code: str) -> list[ClassInfo]:
        """Extract all class definitions from the AST"""
        classes = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self._parse_class(node, source_code)
                classes.append(class_info)

        return classes
    
    def _parse_class(self, node: ast.ClassDef, source_code: str) -> ClassInfo:
        """Parse a single class definition"""
        # Get base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{self._get_attribute_name(base)}")

        # Get decorators 
        decorators = self._extract_decorators(node)

        # Check if it's a dataclass
        is_dataclass = any("dataclass" in d for d in decorators)

        # Get methods
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self._parse_function(item, source_code)
                method_info.element_type = CodeElementType.METHOD
                methods.append(method_info)

        # Get class variables
        class_vars = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                class_vars.append(item.target.id)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_vars.append(target.id)

        return ClassInfo(
            name=node.name,
            bases=bases,
            docstring=ast.get_docstring(node),
            decorators=decorators,
            methods=methods,
            class_variables=class_vars,
            line_number=node.lineno,
            end_line_number=node.end_lineno or node.lineno,
            is_dataclass=is_dataclass
        )
    
    def _extract_functions(
        self,
        tree: ast.Module,
        source_code: str,
        top_level_only: bool = True
    ) -> list[FunctionInfo]:
        """Extract function definitions from the AST"""
        functions = []
        
        nodes = ast.iter_child_nodes(tree) if top_level_only else ast.walk(tree)
        
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = self._parse_function(node, source_code)
                functions.append(func_info)
        
        return functions
    
    def _parse_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, source_code: str) -> FunctionInfo:
        """Parse a single function definition"""

        # Get parameters
        parameters = self._extract_parameters(node.args)

        # Get return type
        return_type = None
        if node.returns:
            return_type = self._annotation_to_string(node.returns)

        # Get decorators
        decorators = self._extract_decorators(node)

        # Check if private
        is_private = node.name.startswith("_")
        
        # Check if async
        is_async = isinstance(node, ast.AsyncFunctionDef)

        # Extract source code for this function
        func_source = None
        if source_code:
            lines = source_code.splitlines()
            start = node.lineno - 1
            end = node.end_lineno or node.lineno
            func_source = "\n".join(lines[start:end])

        return FunctionInfo(
            name=node.name,
            element_type=CodeElementType.ASYNC_FUNCTION if is_async else CodeElementType.FUNCTION,
            parameters=parameters,
            return_type=return_type,
            docstring=ast.get_docstring(node),
            decorators=decorators,
            line_number=node.lineno,
            end_line_number=node.end_lineno or node.lineno,
            is_async=is_async,
            is_private=is_private,
            source_code=func_source
        )

    def _extract_parameters(self, args: ast.arguments) -> list[Parameter]:
        """Extract function parameters"""
        parameters = []

        # Regular args
        defaults_offset = len(args.args) - len(args.defaults)

        for i, arg in enumerate(args.args):
            default_value = None
            default_idx = i - defaults_offset
            if default_idx >= 0 and default_idx < len(args.defaults):
                default_value = self._node_to_string(args.defaults[default_idx])

            param = Parameter(
                name=arg.arg,
                type_hint=self._annotation_to_string(arg.annotation) if arg.annotation else None,
                default_value=default_value
            )
            parameters.append(param)

        # *args
        if args.vararg:
            parameters.append(Parameter(
                name=f"*{args.vararg.arg}",
                type_hint=self._annotation_to_string(args.vararg.annotation) if args.vararg.annotation else None
            ))

        # **kwargs
        if args.kwarg:
            parameters.append(Parameter(
                name=f"**{args.kwarg.arg}",
                type_hint=self._annotation_to_string(args.kwarg.annotation) if args.kwarg.annotation else None
            ))

        return parameters
    
    def _extract_decorators(self, node: ast.FunctionDef | ast.ClassDef) -> list[str]:
        """Extract decorator names"""
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
    
    def _extract_global_variables(self, tree: ast.Module) -> list[str]:
        """Extract global variable names"""
        variables = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    variables.append(node.target.id)
        return variables
    
    def _annotation_to_string(self, node: ast.expr | None) -> str | None:
        """Convert an annotation AST node to string"""
        if node is None:
            return None
        
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Subscript):
            value = self._annotation_to_string(node.value)
            slice_val = self._annotation_to_string(node.slice)
            return f"{value}[{slice_val}]"
        elif isinstance(node, ast.Attribute):
            return self._get_attribute_name(node)
        elif isinstance(node, ast.Tuple):
            elements = ", ".join(
                self._annotation_to_string(e) for e in node.elts
            )
            return elements
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            left = self._annotation_to_string(node.left)
            right = self._annotation_to_string(node.right)
            return f"{left} | {right}"
        
        return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
    
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get full attribute name (e.g., 'module.Class')"""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    
    def _node_to_string(self, node: ast.expr) -> str:
        """Convert an AST node to its string representation"""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.List):
            elements = ", ".join(self._node_to_string(e) for e in node.elts)
            return f"[{elements}]"
        elif isinstance(node, ast.Dict):
            return "{...}"
        
        return ast.unparse(node) if hasattr(ast, 'unparse') else "..."