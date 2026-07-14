# parsers/javascript_parser.py
"""JavaScript/JSX parser using tree-sitter.

Provides a concrete implementation of ``BaseParser`` that parses JavaScript and JSX
source files via the ``tree_sitter`` library. The parser extracts imports, classes,
functions, and JSDoc comments, building the shared ``ParsedFile`` model.

Field names below were verified directly against the installed tree-sitter-javascript
grammar (see inspect_nodes.py) rather than assumed - the grammar does not expose
"property", "superclass", or "async_modifier" fields the way earlier drafts assumed.
"""

import logging
from pathlib import Path
from typing import List, Optional

from tree_sitter import Parser, Language
from tree_sitter_javascript import language as javascript_language

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
    """Return the source text for a tree-sitter node."""
    return source[node.start_byte:node.end_byte].decode("utf-8")


def _is_async(node) -> bool:
    """Check whether a method/function/arrow-function node has a leading
    'async' token. There is no async_modifier field in this grammar -
    async is an unnamed direct child token, so we scan children by type."""
    return any(child.type == "async" for child in node.children)


def _get_base_classes(class_node, source: bytes) -> List[str]:
    """Extract the 'extends' target.

    The extends clause lives inside an unnamed 'class_heritage' child of
    class_declaration - there is no 'superclass' field to read directly."""
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
            # default-valued parameter: name = default
            left = p.child_by_field_name("left")
            right = p.child_by_field_name("right")
            if left:
                params.append(ParameterInfo(
                    name=_node_text(left, source),
                    default_value=_node_text(right, source) if right else None,
                ))
        elif p.type in ("rest_pattern",):
            # ...args
            inner = p.named_children[0] if p.named_children else None
            if inner:
                params.append(ParameterInfo(name=f"*{_node_text(inner, source)}"))
    return params


def _attach_leading_docstring(node, source: bytes) -> Optional[str]:
    """Return the JSDoc comment immediately preceding ``node`` if present.

    Walks backward over preceding siblings; if the nearest preceding sibling
    is a block comment starting with '/**', it is treated as the docstring.
    Any other node type in between means there is no attached docstring.
    """
    prev = node.prev_sibling
    if prev is None or prev.type != "comment":
        return None

    comment_text = _node_text(prev, source).strip()
    if not comment_text.startswith("/**"):
        return None

    # Strip the /** prefix and */ suffix explicitly (not str.strip(), which
    # treats its argument as a character set rather than a literal affix).
    text = comment_text
    if text.startswith("/**"):
        text = text[3:]
    if text.endswith("*/"):
        text = text[:-2]

    lines = text.split("\n")
    cleaned_lines = [line.strip().lstrip("*").strip() for line in lines]
    cleaned = "\n".join(l for l in cleaned_lines if l or True).strip()
    return cleaned or None


class JavaScriptParser(BaseParser):
    """Parse JavaScript/JSX files using tree-sitter.

    Extracts the same structures as the Python AST parser, but for
    JavaScript/JSX source: ES6 imports, CommonJS ``require`` calls,
    classes (including inheritance and arrow-function class fields),
    top-level functions and arrow functions, async variants, and
    JSDoc docstrings.
    """

    def __init__(self, project_root: Optional[str] = None):
        super().__init__(project_root)
        self._parser = Parser()
        self._parser.language = Language(javascript_language())

    @property
    def language(self) -> SourceLanguage:
        return SourceLanguage.JAVASCRIPT

    @property
    def supported_extensions(self) -> List[str]:
        return [".js", ".jsx"]

    # ---------------------------------------------------------------------
    # File handling helpers
    # ---------------------------------------------------------------------
    def _read_source(self, file_path: str) -> bytes:
        full_path = Path(self.project_root) / file_path if self.project_root else Path(file_path)
        return full_path.read_bytes()

    # ---------------------------------------------------------------------
    # Extraction helpers
    # ---------------------------------------------------------------------
    def _extract_imports(self, root, source: bytes) -> List[ImportInfo]:
        imports: List[ImportInfo] = []
        for node in root.children:
            if node.type == "import_statement":
                module_node = node.child_by_field_name("source")
                if module_node:
                    module_name = _node_text(module_node, source).strip("\"'")
                    imports.append(ImportInfo(module=module_name, is_from_import=True))

            if node.type == "expression_statement" and node.named_child_count > 0:
                expr = node.named_children[0]
                if expr.type == "call_expression":
                    function_node = expr.child_by_field_name("function")
                    if function_node and _node_text(function_node, source) == "require":
                        arg_node = expr.child_by_field_name("arguments")
                        if arg_node and arg_node.named_child_count > 0:
                            module_node = arg_node.named_children[0]
                            module_name = _node_text(module_node, source).strip("\"'")
                            imports.append(ImportInfo(module=module_name, is_from_import=False))

            # const x = require('module') - common CommonJS pattern
            if node.type in ("lexical_declaration", "variable_declaration"):
                for declarator in node.named_children:
                    if declarator.type != "variable_declarator":
                        continue
                    value = declarator.child_by_field_name("value")
                    if value and value.type == "call_expression":
                        fn = value.child_by_field_name("function")
                        if fn and _node_text(fn, source) == "require":
                            args = value.child_by_field_name("arguments")
                            if args and args.named_child_count > 0:
                                module_name = _node_text(args.named_children[0], source).strip("\"'")
                                imports.append(ImportInfo(module=module_name, is_from_import=False))
        return imports

    def _extract_class_members(self, class_node, source: bytes) -> List[FunctionInfo]:
        methods: List[FunctionInfo] = []
        body = class_node.child_by_field_name("body")
        if not body:
            return methods

        for child in body.children:
            if child.type == "method_definition":
                name_node = child.child_by_field_name("name")  # verified field: "name"
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

            elif child.type == "field_definition":  # verified type: field_definition, not public_field_definition
                name_node = child.child_by_field_name("property")  # verified field: "property"
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
                classes.append(ClassInfo(
                    name=class_name,
                    docstring=_attach_leading_docstring(node, source),
                    methods=self._extract_class_members(node, source),
                    base_classes=_get_base_classes(node, source),
                    decorators=[],
                    class_variables=[],
                    line_number=node.start_point[0] + 1,
                ))
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
                    is_private=func_name.startswith("_"),
                    line_number=node.start_point[0] + 1,
                ))

            if node.type in ("lexical_declaration", "variable_declaration"):
                for declarator in node.named_children:
                    if declarator.type != "variable_declarator":
                        continue
                    name_node = declarator.child_by_field_name("name")
                    init_node = declarator.child_by_field_name("value")
                    if not name_node or not init_node:
                        continue
                    if init_node.type in ("arrow_function", "function"):
                        func_name = _node_text(name_node, source)
                        params_node = init_node.child_by_field_name("parameters")
                        functions.append(FunctionInfo(
                            name=func_name,
                            params=_extract_params(params_node, source),
                            returns=None,
                            docstring=_attach_leading_docstring(node, source),
                            decorators=[],
                            is_async=_is_async(init_node),
                            is_private=func_name.startswith("_"),
                            line_number=declarator.start_point[0] + 1,
                        ))
        return functions

    def _detect_entry_point(self, root, source: bytes) -> bool:
        """Detect `if (require.main === module)` style entry-point checks."""
        for node in root.children:
            if node.type == "if_statement":
                condition = node.child_by_field_name("condition")
                if condition:
                    cond_text = _node_text(condition, source)
                    if "require.main" in cond_text and "module" in cond_text:
                        return True
        return False

    def _has_parse_errors(self, root) -> bool:
        if root.type == "ERROR" or root.has_error:
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

        try:
            tree = self._parser.parse(source)
        except Exception as e:
            logger.warning(f"Tree-sitter failed to parse {file_path}: {e}")
            return None

        root = tree.root_node

        if self._has_parse_errors(root):
            logger.warning(
                f"Tree-sitter reported syntax errors in {file_path}; "
                f"extraction may be incomplete for this file."
            )

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
            language=SourceLanguage.JAVASCRIPT,
        )

    def parse_files(self, file_paths: List[str]) -> List[ParsedFile]:
        results: List[ParsedFile] = []
        for fp in file_paths:
            parsed = self.parse_file(fp)
            if parsed:
                results.append(parsed)
        return results


if __name__ == "__main__":
    # Manual test - exercises: inherited class, named async method,
    # arrow-function class property, top-level arrow function,
    # top-level function declaration, JSDoc docstrings, entry-point check.
    sample = """
/**
 * Sample class documentation
 */
class Base {}
class MyClass extends Base {
    /** method doc */
    async myMethod(param1, param2) {}
    /** arrow property doc */
    arrowProp = async () => {};
}
// top-level arrow function
const topArrow = (a, b) => a + b;
// top-level function
function topFunc(x) { return x; }
if (require.main === module) {
    console.log('entry');
}
"""
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(delete=False, suffix=".js", mode="w", encoding="utf-8") as f:
        f.write(sample)
        path = f.name

    parser = JavaScriptParser()
    parsed = parser.parse_file(path)

    print(f"File: {parsed.file_path}")
    print(f"Lines: {parsed.line_count}")
    print(f"Entry Point: {parsed.has_entry_point}")

    print(f"\nImports ({len(parsed.imports)}):")
    for imp in parsed.imports:
        print(f"  - {imp}")

    print(f"\nClasses ({len(parsed.classes)}):")
    for cls in parsed.classes:
        print(f"  - {cls.name}")
        print(f"    Docstring: {cls.docstring!r}")
        print(f"    Bases: {cls.base_classes}")
        print(f"    Methods:")
        for m in cls.methods:
            print(f"      - {m.name}(async={m.is_async}) doc={m.docstring!r} params={[p.name for p in m.params]}")

    print(f"\nFunctions ({len(parsed.functions)}):")
    for func in parsed.functions:
        print(f"  - {func.name}(async={func.is_async}) doc={func.docstring!r} params={[p.name for p in func.params]}")