# parsers/typescript_parser.py
"""TypeScript/TSX parser using tree-sitter.

Mirrors javascript_parser.py, but the TypeScript grammar is NOT identical to the
JavaScript grammar - verified via inspect_ts_nodes.py against the real installed
grammar. Key differences from JS:
  - Typed parameters are wrapped in `required_parameter` / `optional_parameter`
    nodes with `pattern` and `type` fields, not bare `identifier` nodes.
  - Class fields use type `public_field_definition`, not `field_definition`.
  - `extends` lives in `class_heritage` -> `extends_clause` (field `value`),
    not a bare identifier directly under `class_heritage`.
No regex fallback - all extraction is done via grammar node types/fields.
"""

import sys
import logging
from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tree_sitter import Parser, Language
from tree_sitter_typescript import language_typescript, language_tsx

from parsers.base_parser import BaseParser
from models.parsed_file import (
    InterfaceInfo,
    PropertyInfo,
    EnumInfo,
    TypeAliasInfo,
    ParsedFile,
    ImportInfo,
    ClassInfo,
    FunctionInfo,
    ParameterInfo,
    ExportInfo,
)
from models.language import SourceLanguage

logger = logging.getLogger(__name__)


def _node_text(node, source: bytes) -> str:
    return source[node.start_byte:node.end_byte].decode("utf-8")


def _is_async(node) -> bool:
    """async is an unnamed leading child token, same as in the JS grammar."""
    return any(child.type == "async" for child in node.children)


def _get_base_classes(class_node, source: bytes) -> List[str]:
    """extends lives in class_heritage -> extends_clause (field 'value'),
    not directly under class_heritage as in the JS grammar."""
    bases: List[str] = []
    for child in class_node.children:
        if child.type == "class_heritage":
            for gc in child.children:
                if gc.type == "extends_clause":
                    value_node = gc.child_by_field_name("value")
                    if value_node:
                        bases.append(_node_text(value_node, source))
    return bases


def _extract_params(params_node, source: bytes) -> List[ParameterInfo]:
    """TS wraps each parameter in required_parameter / optional_parameter,
    with the actual name under field 'pattern' and the type under field
    'type' (a type_annotation node, e.g. ': string'). Plain 'identifier'
    params (untyped, rare in .ts but valid) are also handled as a fallback
    node type, matching the JS grammar shape."""
    if not params_node:
        return []
    params: List[ParameterInfo] = []
    for p in params_node.named_children:
        if p.type in ("required_parameter", "optional_parameter"):
            pattern_node = p.child_by_field_name("pattern")
            type_node = p.child_by_field_name("type")
            value_node = p.child_by_field_name("value")  # default value, if any
            if pattern_node is None:
                continue
            name = _node_text(pattern_node, source)
            type_hint = None
            if type_node:
                # type_annotation text includes the leading ':' - strip it
                raw = _node_text(type_node, source)
                type_hint = raw[1:].strip() if raw.startswith(":") else raw.strip()
            default_value = _node_text(value_node, source) if value_node else None
            params.append(ParameterInfo(
                name=name,
                type_hint=type_hint,
                default_value=default_value,
            ))
        elif p.type == "identifier":
            params.append(ParameterInfo(name=_node_text(p, source)))
        elif p.type == "assignment_pattern":
            left = p.child_by_field_name("left")
            right = p.child_by_field_name("right")
            if left:
                params.append(ParameterInfo(
                    name=_node_text(left, source),
                    default_value=_node_text(right, source) if right else None,
                ))
        elif p.type == "rest_pattern":
            inner = p.named_children[0] if p.named_children else None
            if inner:
                params.append(ParameterInfo(name=f"*{_node_text(inner, source)}"))
    return params


def _attach_leading_docstring(node, source: bytes) -> Optional[str]:
    """Same approach validated for the JS parser: only the immediately
    preceding sibling counts, and it must be a /** */ block comment."""
    prev = node.prev_sibling
    if prev is None or prev.type != "comment":
        return None

    comment_text = _node_text(prev, source).strip()
    if not comment_text.startswith("/**"):
        return None

    text = comment_text
    if text.startswith("/**"):
        text = text[3:]
    if text.endswith("*/"):
        text = text[:-2]

    lines = text.split("\n")
    cleaned_lines = [line.strip().lstrip("*").strip() for line in lines]
    cleaned = "\n".join(l for l in cleaned_lines if l or True).strip()
    return cleaned or None


class TypeScriptParser(BaseParser):
    """Parse TypeScript/TSX files using tree-sitter.

    Uses the dedicated TS grammar for .ts and the TSX grammar for .tsx,
    since JSX syntax requires the separate tsx grammar variant.
    """

    def __init__(self, project_root: Optional[str] = None):
        super().__init__(project_root)
        self._ts_parser = Parser()
        self._ts_parser.language = Language(language_typescript())
        self._tsx_parser = Parser()
        self._tsx_parser.language = Language(language_tsx())

    @property
    def language(self) -> SourceLanguage:
        return SourceLanguage.TYPESCRIPT

    @property
    def supported_extensions(self) -> List[str]:
        return [".ts", ".tsx"]

    def _read_source(self, file_path: str) -> bytes:
        full_path = Path(self.project_root) / file_path if self.project_root else Path(file_path)
        return full_path.read_bytes()

    def _parser_for_file(self, file_path: str) -> Parser:
        ext = Path(file_path).suffix.lower()
        return self._tsx_parser if ext == ".tsx" else self._ts_parser

    # ---------------------------------------------------------------------
    # Extraction helpers
    # ---------------------------------------------------------------------
    def _extract_imports(self, root, source: bytes) -> List[ImportInfo]:
        imports: List[ImportInfo] = []
        for node in root.children:
            if node.type == "import_statement":
                module_node = node.child_by_field_name("source")
                import_clause = node.child_by_field_name("import_clause")
                names = []
                if import_clause:
                    for child in import_clause.named_children:
                        if child.type == "named_imports":
                            for spec in child.named_children:
                                if spec.type == "import_specifier":
                                    name_node = spec.child_by_field_name("name")
                                    if name_node:
                                        names.append(_node_text(name_node, source))
                        elif child.type == "namespace_import":
                            name_node = child.child_by_field_name("name")
                            if name_node:
                                names.append(_node_text(name_node, source))
                imports.append(ImportInfo(module=module_name, names=names, is_from_import=True))
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
                name_node = child.child_by_field_name("name")
                method_name = _node_text(name_node, source) if name_node else "<anonymous>"
                params_node = child.child_by_field_name("parameters")
                return_type = child.child_by_field_name("return_type")
                returns = _node_text(return_type, source=source).strip() if return_type else None
                body_node = child.child_by_field_name("body")
                body_text = _node_text(body_node, source) if body_node else None
                methods.append(FunctionInfo(
                    name=method_name,
                    params=_extract_params(params_node, source),
                    returns=returns,
                    body=body_text,
                    docstring=_attach_leading_docstring(child, source),
                    decorators=[],
                    is_async=_is_async(child),
                    is_private=method_name.startswith("_"),
                    line_number=child.start_point[0] + 1,
                ))

            # verified: TS uses public_field_definition, NOT field_definition
            elif child.type == "public_field_definition":
                name_node = child.child_by_field_name("name")
                field_name = _node_text(name_node, source) if name_node else "<anonymous>"
                value_node = child.child_by_field_name("value")
                if value_node and value_node.type in ("arrow_function", "function"):
                    params_node = value_node.child_by_field_name("parameters")
                    methods.append(FunctionInfo(
                        name=field_name,
                        params=_extract_params(params_node, source),
                        returns=returns,
                        docstring=_attach_leading_docstring(child, source),
                        decorators=[],
                        is_async=_is_async(value_node),
                        is_private=field_name.startswith("_"),
                        line_number=child.start_point[0] + 1,
                    ))
        return methods

    def _extract_classes(self, root, source: bytes) -> List[ClassInfo]:
        classes: List[ClassInfo] = []
        for node, is_exported in self._iter_top_level_declarations(root):
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
                    is_exported=is_exported,
                    line_number=node.start_point[0] + 1,
                ))
        return classes

    def _extract_functions(self, root, source: bytes) -> List[FunctionInfo]:
        functions: List[FunctionInfo] = []
        for node, is_exported in self._iter_top_level_declarations(root):
            if node.type == "function_declaration":
                name_node = node.child_by_field_name("name")
                func_name = _node_text(name_node, source) if name_node else "<anonymous>"
                params_node = node.child_by_field_name("parameters")
                return_type = node.child_by_field_name("return_type")
                returns = _node_text(return_type, source=source).strip() if return_type else None
                node_body = node.child_by_field_name("body")
                body_text = _node_text(node_body, source) if node_body else None
                functions.append(FunctionInfo(
                    name=func_name,
                    params=_extract_params(params_node, source),
                    returns=returns,
                    body=body_text,
                    docstring=_attach_leading_docstring(node, source),
                    decorators=[],
                    is_async=_is_async(node),
                    is_private=func_name.startswith("_"),
                    is_exported=is_exported,
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
                        body_text = _node_text(init_node.child_by_field_name("body"), source) if init_node.child_by_field_name("body") else None
                        functions.append(FunctionInfo(
                            name=func_name,
                            params=_extract_params(params_node, source),
                            returns=returns,
                            body=body_text,
                            docstring=_attach_leading_docstring(node, source),
                            decorators=[],
                            is_async=_is_async(init_node),
                            is_private=func_name.startswith("_"),
                            is_exported=is_exported,
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

    def _has_parse_errors(self, root) -> bool:
        return root.type == "ERROR" or root.has_error

    def _iter_top_level_declarations(self, root):
            """
            Yield (node, is_exported) for top-level declarations,
            including those wrapped in export_statement.
            """
            for child in root.children:
                if child.type == "export_statement":
                    decl = child.child_by_field_name("declaration")
                    if decl:
                        yield decl, True
                        continue
    
                    value = child.child_by_field_name("value")
                    if value:
                        yield value, True
                        continue
    
                else:
                    yield child, False
    
    def _extract_exports(self, root, source: bytes) -> List[ExportInfo]:
        exports = []
        for child in root.children:
            if child.type != "export_statement":
                continue

            # Handle `export class/function/const/let/var ...`
            declaration = child.child_by_field_name("declaration")
            if declaration:
                kind = declaration.type
                name = None

                if declaration.type == "class_declaration":
                    name_node = declaration.child_by_field_name("name")
                    name = _node_text(name_node, source) if name_node else "<anonymous>"
                elif declaration.type == "function_declaration":
                    name_node = declaration.child_by_field_name("name")
                    name = _node_text(name_node, source) if name_node else "<anonymous>"
                elif declaration.type in ("lexical_declaration", "variable_declaration"):
                    declarator = next(
                        (d for d in declaration.named_children if d.type == "variable_declarator"),
                        None
                    )
                    if declarator:
                        name_node = declarator.child_by_field_name("name")
                        name = _node_text(name_node, source) if name_node else "<anonymous>"
                if name:
                    exports.append(ExportInfo(
                        name=name,
                        kind=kind,
                        line_number=child.start_point[0] + 1,
                    ))
                continue

            # Handle `export { foo, bar as baz }`
            for sub_child in child.children:
                if sub_child.type == "export_clause":
                    for spec in sub_child.named_children:
                        if spec.type == "export_specifier":
                            name_node = spec.child_by_field_name("name")
                            alias_node = spec.child_by_field_name("alias")
                            name = _node_text(name_node, source) if name_node else "<anonymous>"
                            alias = _node_text(alias_node, source) if alias_node else None
                            exports.append(ExportInfo(
                                name=name,
                                kind="named",
                                line_number=spec.start_point[0] + 1,
                            ))

            # Handle `export * from './mod'` or `export { foo } from './mod'`
            source_node = child.child_by_field_name("source")
            if source_node:
                module_name = _node_text(source_node, source).strip("\"'")
                exports.append(ExportInfo(
                    name="*",
                    kind="reexport",
                    source=module_name,
                    line_number=child.start_point[0] + 1,
                ))
                continue

            # Handle default export: `export default function/class/expression`
            value = child.child_by_field_name("value")
            if value:
                name = None
                if value.type in ("class_declaration", "function_declaration"):
                    name_node = value.child_by_field_name("name")
                    name = _node_text(name_node, source) if name_node else "<anonymous>"
                else:
                    name = _node_text(value, source)
                exports.append(ExportInfo(
                    name=name,
                    kind="default",
                    line_number=child.start_point[0] + 1,
                ))

        return exports

    def _extract_interfaces(self, root, source: bytes) -> List[InterfaceInfo]:
        interfaces: List[InterfaceInfo] = []
        for node, is_exported in self._iter_top_level_declarations(root):
            if node.type == "interface_declaration":
                name_node = node.child_by_field_name("name")
                interface_name = _node_text(name_node, source) if name_node else "<anonymous>"
                properties: List[PropertyInfo] = []
                extends: List[str] = []

                heritage_node = node.child_by_field_name("heritage")
                if heritage_node:
                    for ext in heritage_node.named_children:
                        if ext.type == "extends_clause":
                            value_node = ext.child_by_field_name("value")
                            if value_node:
                                extends.append(_node_text(value_node, source))

                body_node = node.child_by_field_name("body")
                if body_node:
                    for member in body_node.named_children:
                        if member.type == "property_signature":
                            prop_name_node = member.child_by_field_name("name")
                            type_node = member.child_by_field_name("type")
                            prop_name = _node_text(prop_name_node, source) if prop_name_node else "<anonymous>"
                            type_hint = _node_text(type_node, source) if type_node else None
                            properties.append(PropertyInfo(
                                name=prop_name,
                                type_hint=type_hint,
                                visibility=None,
                                is_static=False,
                                is_readonly=False,
                                has_default=False
                            ))

                interfaces.append(InterfaceInfo(
                    name=interface_name,
                    properties=properties,
                    extends=extends,
                    line_number=node.start_point[0] + 1
                ))
        return interfaces

    def _extract_type_aliases(self, root, source: bytes) -> List[TypeAliasInfo]:
        type_aliases: List[TypeAliasInfo] = []
        for node, is_exported in self._iter_top_level_declarations(root):
            if node.type == "type_alias_declaration":
                name_node = node.child_by_field_name("name")
                type_node = node.child_by_field_name("type")
                alias_name = _node_text(name_node, source) if name_node else "<anonymous>"
                type_text = _node_text(type_node, source) if type_node else ""
                type_aliases.append(TypeAliasInfo(
                    name=alias_name,
                    type_text=type_text,
                    line_number=node.start_point[0] + 1
                ))
        return type_aliases

    def _extract_enums(self, root, source: bytes) -> List[EnumInfo]:
        enums: List[EnumInfo] = []
        for node, is_exported in self._iter_top_level_declarations(root):
            if node.type == "enum_declaration":
                name_node = node.child_by_field_name("name")
                enum_name = _node_text(name_node, source) if name_node else "<anonymous>"
                enums.append(EnumInfo(
                    name=enum_name
                ))
        return enums

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def parse_file(self, file_path: str) -> Optional[ParsedFile]:
        try:
            source = self._read_source(file_path)
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")
            return None

        parser = self._parser_for_file(file_path)
        try:
            tree = parser.parse(source)
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
        interfaces = self._extract_interfaces(root, source)
        type_aliases = self._extract_type_aliases(root, source)
        enums = self._extract_enums(root, source)
        line_count = source.count(b"\n") + 1
        has_entry = self._detect_entry_point(root, source)
        exports = self._extract_exports(root, source)

        return ParsedFile(
            file_path=file_path,
            module_docstring=None,
            imports=imports,
            classes=classes,
            functions=functions,
            global_variables=[],
            line_count=line_count,
            has_entry_point=has_entry,
            exports=exports,
            language=SourceLanguage.TYPESCRIPT,
            interfaces=interfaces,
            type_aliases=type_aliases,
            enums=enums,
        )

    def parse_files(self, file_paths: List[str]) -> List[ParsedFile]:
        results: List[ParsedFile] = []
        for fp in file_paths:
            parsed = self.parse_file(fp)
            if parsed:
                results.append(parsed)
        return results


if __name__ == "__main__":
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

export interface User {
  id: string;
  email: string;
}

export async function fetchUser(id: string): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  return res.json();
}

export class UserService {
  private baseUrl = "/api";
  async getUser(id: string) {
    return fetchUser(id);
  }
}

const helper = () => {};
export { helper };
"""
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(delete=False, suffix=".ts", mode="w", encoding="utf-8") as f:
        f.write(sample_ts)
        path = f.name

    parser = TypeScriptParser()
    parsed = parser.parse_file(path)

    print(f"File: {parsed.file_path}")
    print(f"Lines: {parsed.line_count}")
    print(f"Entry Point: {parsed.has_entry_point}")

    print(f"\nClasses ({len(parsed.classes)}):")
    for cls in parsed.classes:
        print(f"  - {cls.name}  bases={cls.base_classes}  doc={cls.docstring!r}")
        for m in cls.methods:
            print(f"      - {m.name}(async={m.is_async}) doc={m.docstring!r} "
                  f"params={[(p.name, p.type_hint) for p in m.params]}")

    print(f"\nFunctions ({len(parsed.functions)}):")
    for func in parsed.functions:
        print(f"  - {func.name}(async={func.is_async}) "
              f"params={[(p.name, p.type_hint) for p in func.params]}")

    print(f"\nExports ({len(parsed.exports)}):")
    for exp in parsed.exports:
        print(f"  - {exp.name} (kind={exp.kind})")