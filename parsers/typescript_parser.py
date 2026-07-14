# parsers/typescript_parser.py
"""TypeScript/TSX parser using tree-sitter.

Provides a concrete ``BaseParser`` implementation that parses TypeScript and TSX files
using the ``tree_sitter`` library (via ``tree_sitter_typescript``). Extraction mirrors
the JavaScript parser: imports, classes (including inheritance and arrow‑function class
fields), top‑level functions (declarations and arrow functions), async variants, and
JSDoc comments.
"""

import logging
from pathlib import Path
from typing import List, Optional
import re

from tree_sitter import Parser, Language
from tree_sitter_typescript import language_typescript, language_tsx

from parsers.base_parser import BaseParser
from models.parsed_file import (
    ParsedFile,
    ImportInfo,
    ClassInfo,
    FunctionInfo,
    ParameterInfo,
)
from models.language import SourceLanguage

logger = logging.getLogger(__name__)


def _node_text(node, source: bytes) -> str:
    """Return the source text for a tree‑sitter node."""
    return source[node.start_byte : node.end_byte].decode("utf-8")


def _attach_leading_docstring(node, source: bytes) -> Optional[str]:
    """Return a JSDoc comment immediately preceding ``node`` if present.

    Walks backwards over named siblings until a block comment starting with ``/**``
    is found, then strips delimiters and leading ``*`` characters.
    """
    prev = node.prev_named_sibling
    while prev:
        if prev.type == "comment":
            comment = _node_text(prev, source)
            if comment.startswith('/**'):
                lines = comment.strip('/**/').split('\n')
                cleaned = "\n".join(line.lstrip(' *') for line in lines).strip()
                return cleaned
        if prev.type not in {"comment", "program"}:
            break
        prev = prev.prev_named_sibling
    return None


def _is_async(node) -> bool:
    return any(child.type == "async" for child in node.children)


def _get_base_classes(class_node, source: bytes) -> List[str]:
    bases: List[str] = []
    for child in class_node.children:
        if child.type == "class_heritage":
            for gc in child.children:
                if gc.type in ("identifier", "member_expression"):
                    bases.append(_node_text(gc, source))
    return bases


def _extract_params(params_node, source: bytes) -> List[ParameterInfo]:
    if not params_node:
        return []
    params: List[ParameterInfo] = []
    for p in params_node.named_children:
        if p.type == "identifier":
            params.append(ParameterInfo(name=_node_text(p, source)))
        elif p.type == "assignment_pattern":
            left = p.child_by_field_name("left")
            right = p.child_by_field_name("right")
            if left:
                params.append(ParameterInfo(
                    name=_node_text(left, source),
                    default_value=_node_text(right, source) if right else None,
                ))
        elif p.type in ("rest_pattern",):
            inner = p.named_children[0] if p.named_children else None
            if inner:
                params.append(ParameterInfo(name=f"*{_node_text(inner, source)}"))
    # Fallback: some grammars wrap parameter nodes differently (typed params like "a: string").
    if not params and params_node is not None:
        raw = _node_text(params_node, source).strip()
        # Strip surrounding parentheses if present
        if raw.startswith("(") and raw.endswith(")"):
            raw = raw[1:-1]
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        for part in parts:
            # remove default assignment and type annotations
            # match leading identifier possibly prefixed by '...'
            m = re.match(r'^(?:\.\.\.)?([A-Za-z_][A-Za-z0-9_]*)', part)
            if m:
                params.append(ParameterInfo(name=m.group(1)))

    return params


class TypeScriptParser(BaseParser):
    """Parse TypeScript/TSX files using tree‑sitter.

    The parser follows the same extraction strategy as ``JavaScriptParser`` but
    uses the TypeScript grammar. It supports both ``.ts`` and ``.tsx`` extensions.
    """

    def __init__(self, project_root: Optional[str] = None):
        super().__init__(project_root)
        self._parser = Parser()
        # Default language; will be switched per file if needed
        self._parser.language = Language(language_typescript())

    @property
    def language(self) -> SourceLanguage:
        return SourceLanguage.TYPESCRIPT

    @property
    def supported_extensions(self) -> List[str]:
        return [".ts", ".tsx"]

    # ---------------------------------------------------------------------
    # File handling helpers
    # ---------------------------------------------------------------------
    def _read_source(self, file_path: str) -> bytes:
        full_path = Path(self.project_root) / file_path if self.project_root else Path(file_path)
        return full_path.read_bytes()

    def _set_language_for_file(self, file_path: str):
        ext = Path(file_path).suffix.lower()
        if ext == ".tsx":
            self._parser.language = Language(language_tsx())
        else:
            self._parser.language = Language(language_typescript())

    # ---------------------------------------------------------------------
    # Extraction helpers – similar to JavaScriptParser but using TypeScript grammar
    # ---------------------------------------------------------------------
    def _extract_imports(self, root, source: bytes) -> List[ImportInfo]:
        imports: List[ImportInfo] = []
        for node in root.children:
            if node.type == "import_statement":
                module_node = node.child_by_field_name("source")
                if module_node:
                    module_name = _node_text(module_node, source).strip('"\'')
                    imports.append(ImportInfo(module=module_name, is_from_import=True))
            if node.type == "expression_statement" and node.child_by_field_name("expression"):
                expr = node.child_by_field_name("expression")
                if expr.type == "call_expression":
                    function_node = expr.child_by_field_name("function")
                    if function_node and _node_text(function_node, source) == "require":
                        arg_node = expr.child_by_field_name("arguments")
                        if arg_node and arg_node.named_child_count > 0:
                            module_node = arg_node.named_children[0]
                            module_name = _node_text(module_node, source).strip('"\'')
                            imports.append(ImportInfo(module=module_name, is_from_import=False))
        return imports

    def _extract_class_members(self, class_node, source: bytes) -> List[FunctionInfo]:
        methods: List[FunctionInfo] = []
        body = class_node.child_by_field_name("body")
        if not body:
            return methods

        for child in body.children:
            if child.type == "method_definition":
                name_node = child.child_by_field_name("name")
                method_name = _node_text(name_node, source) if name_node else "<anonymous>"
                params_node = child.child_by_field_name("parameters")
                methods.append(FunctionInfo(
                    name=method_name,
                    params=_extract_params(params_node, source),
                    returns=None,
                    docstring=_attach_leading_docstring(child, source),
                    decorators=[],
                    is_async=_is_async(child),
                    is_private=method_name.startswith("_"),
                    line_number=child.start_point[0] + 1,
                ))

            elif child.type == "field_definition":
                name_node = child.child_by_field_name("property")
                field_name = _node_text(name_node, source) if name_node else "<anonymous>"
                value_node = child.child_by_field_name("value")
                if value_node and value_node.type in ("arrow_function", "function"):
                    params_node = value_node.child_by_field_name("parameters")
                    methods.append(FunctionInfo(
                        name=field_name,
                        params=_extract_params(params_node, source),
                        returns=None,
                        docstring=_attach_leading_docstring(child, source),
                        decorators=[],
                        is_async=_is_async(value_node),
                        is_private=field_name.startswith("_"),
                        line_number=child.start_point[0] + 1,
                    ))
        return methods

    def _extract_classes(self, root, source: bytes) -> List[ClassInfo]:
        classes: List[ClassInfo] = []
        for node in root.children:
            if node.type == "class_declaration":
                name_node = node.child_by_field_name("name")
                class_name = _node_text(name_node, source) if name_node else "<anonymous>"
                classes.append(
                    ClassInfo(
                        name=class_name,
                        docstring=_attach_leading_docstring(node, source),
                        methods=self._extract_class_members(node, source),
                        base_classes=_get_base_classes(node, source),
                        decorators=[],
                        class_variables=[],
                        line_number=node.start_point[0] + 1,
                    )
                )
        return classes

    def _extract_functions(self, root, source: bytes) -> List[FunctionInfo]:
        functions: List[FunctionInfo] = []
        for node in root.children:
            if node.type == "function_declaration":
                name_node = node.child_by_field_name("name")
                func_name = _node_text(name_node, source) if name_node else "<anonymous>"
                params_node = node.child_by_field_name("parameters")
                functions.append(FunctionInfo(
                    name=func_name,
                    params=_extract_params(params_node, source),
                    returns=None,
                    docstring=_attach_leading_docstring(node, source),
                    decorators=[],
                    is_async=_is_async(node),
                    is_private=func_name.startswith('_'),
                    line_number=node.start_point[0] + 1,
                ))

            if node.type in {"lexical_declaration", "variable_declaration"}:
                for declarator in node.named_children:
                    if declarator.type != "variable_declarator":
                        continue
                    name_node = declarator.child_by_field_name("name")
                    init_node = declarator.child_by_field_name("value")
                    if not name_node or not init_node:
                        continue
                    func_name = _node_text(name_node, source)
                    if init_node.type in {"arrow_function", "function"}:
                        param_node = init_node.child_by_field_name("parameters")
                        functions.append(FunctionInfo(
                            name=func_name,
                            params=_extract_params(param_node, source),
                            returns=None,
                            docstring=_attach_leading_docstring(declarator, source),
                            decorators=[],
                            is_async=_is_async(init_node),
                            is_private=func_name.startswith('_'),
                            line_number=declarator.start_point[0] + 1,
                        ))
        return functions

    def _detect_entry_point(self, root, source: bytes) -> bool:
        for node in root.children:
            if node.type == "if_statement":
                condition = node.child_by_field_name("condition")
                if condition:
                    cond_text = _node_text(condition, source)
                    if "require.main" in cond_text and "module" in cond_text:
                        return True
        return False

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def parse_file(self, file_path: str) -> Optional[ParsedFile]:
        try:
            source = self._read_source(file_path)
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")
            return None
        self._set_language_for_file(file_path)
        try:
            tree = self._parser.parse(source)
        except Exception as e:
            logger.warning(f"Tree-sitter failed to parse {file_path}: {e}")
            return None
        root = tree.root_node
        if any(child.type == "ERROR" for child in root.children):
            logger.warning(f"Tree‑sitter reported syntax errors in {file_path}")
        imports = self._extract_imports(root, source)
        classes = self._extract_classes(root, source)
        functions = self._extract_functions(root, source)
        line_count = source.count(b"\n") + 1
        has_entry = self._detect_entry_point(root, source)
        return ParsedFile(
            file_path=file_path,
            module_docstring=None,
            imports=imports,
            classes=classes,
            functions=functions,
            global_variables=[],
            line_count=line_count,
            has_entry_point=has_entry,
            language=SourceLanguage.TYPESCRIPT,
        )

    def parse_files(self, file_paths: List[str]) -> List[ParsedFile]:
        results: List[ParsedFile] = []
        for fp in file_paths:
            parsed = self.parse_file(fp)
            if parsed:
                results.append(parsed)
        return results

if __name__ == "__main__":
    # Quick manual test for TypeScript parsing
    sample_ts = """
    /** Sample class */
    class Base {}
    class MyClass extends Base {
        /** method doc */
        async myMethod(param: string) {}
        /** arrow prop doc */
        arrowProp = async () => {};
    }
    const topArrow = (a: number, b: number) => a + b;
    function topFunc(x: number) { return x; }
    if (require.main === module) { console.log('entry'); }
    """
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(delete=False, suffix=".ts", mode="w", encoding="utf-8") as f:
        f.write(sample_ts)
        path = f.name
    parser = TypeScriptParser()
    parsed = parser.parse_file(path)
    print(parsed)
