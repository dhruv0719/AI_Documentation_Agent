# test/test_parsers.py
"""Test matrix for parsers/python_parser.py, javascript_parser.py, typescript_parser.py.

Two layers:
1. Snapshot tests - full ParsedFile structure vs. a checked-in expected dict.
   Catches ANY structural drift (renamed field misread, missed node type,
   wrong extraction) across the whole fixture in one assertion.
2. Targeted edge-case tests - specific regressions this project already hit
   once (docstring leak, wrong field name, missed node type) get their own
   named test so a failure points directly at the bug, not just "snapshot
   mismatch, go diff 40 lines".

Run with: pytest tests/ -v
"""

import logging
from pathlib import Path

import pytest

from parsers.python_parser import PythonParser
from parsers.javascript_parser import JavaScriptParser
from parsers.typescript_parser import TypeScriptParser
from test.serialize import serialize_parsed_file
from test.snapshot import SNAPSHOTS

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _parse(parser_cls, filename):
    parser = parser_cls(project_root=str(FIXTURES_DIR))
    result = parser.parse_file(filename)
    assert result is not None, f"{parser_cls.__name__} returned None for {filename} - parse failed entirely"
    return result


# ---------------------------------------------------------------------
# Layer 1: full-structure snapshot tests
# ---------------------------------------------------------------------

@pytest.mark.parametrize("language,parser_cls,filename", [
    ("python", PythonParser, "sample.py"),
    ("javascript", JavaScriptParser, "sample.js"),
    ("typescript", TypeScriptParser, "sample.ts"),
])
def test_snapshot(language, parser_cls, filename):
    parsed = _parse(parser_cls, filename)
    actual = serialize_parsed_file(parsed)
    expected = SNAPSHOTS[language]
    assert actual == expected, (
        f"\n--- Snapshot mismatch for {language} ({filename}) ---\n"
        f"Expected: {expected}\n"
        f"Actual:   {actual}\n"
    )


# ---------------------------------------------------------------------
# Layer 2: targeted edge-case regressions
# ---------------------------------------------------------------------

# ---- inheritance / base_classes ----

@pytest.mark.parametrize("parser_cls,filename", [
    (PythonParser, "sample.py"),
    (JavaScriptParser, "sample.js"),
    (TypeScriptParser, "sample.ts"),
])
def test_inheritance_detected(parser_cls, filename):
    parsed = _parse(parser_cls, filename)
    my_class = next(c for c in parsed.classes if c.name == "MyClass")
    assert my_class.base_classes == ["Base"], (
        f"base_classes extraction broken for {parser_cls.__name__}: got {my_class.base_classes}"
    )


# ---- docstring non-leak across back-to-back declarations ----

@pytest.mark.parametrize("parser_cls,filename", [
    (PythonParser, "sample.py"),
    (JavaScriptParser, "sample.js"),
    (TypeScriptParser, "sample.ts"),
])
def test_no_docstring_leak_between_classes(parser_cls, filename):
    parsed = _parse(parser_cls, filename)
    no_doc_class = next(c for c in parsed.classes if c.name == "NoDocClass")
    assert no_doc_class.docstring is None, (
        f"docstring leaked from a preceding class into NoDocClass for {parser_cls.__name__}: "
        f"got {no_doc_class.docstring!r}"
    )


# ---- async detection ----

@pytest.mark.parametrize("parser_cls,filename,method_name", [
    (PythonParser, "sample.py", "async_method"),
    (JavaScriptParser, "sample.js", "asyncMethod"),
    (TypeScriptParser, "sample.ts", "asyncMethod"),
])
def test_async_method_detected(parser_cls, filename, method_name):
    parsed = _parse(parser_cls, filename)
    my_class = next(c for c in parsed.classes if c.name == "MyClass")
    method = my_class.methods[method_name] if isinstance(my_class.methods, dict) else \
        next(m for m in my_class.methods if m.name == method_name)
    assert method.is_async is True, f"{method_name} should be is_async=True for {parser_cls.__name__}"


# ---- arrow-function / assigned class property counted as a method (JS/TS only) ----

@pytest.mark.parametrize("parser_cls,filename", [
    (JavaScriptParser, "sample.js"),
    (TypeScriptParser, "sample.ts"),
])
def test_arrow_class_property_captured(parser_cls, filename):
    parsed = _parse(parser_cls, filename)
    my_class = next(c for c in parsed.classes if c.name == "MyClass")
    names = [m.name for m in my_class.methods]
    assert "arrowProp" in names, (
        f"arrow-function class property not captured for {parser_cls.__name__}: methods found = {names}"
    )


# ---- private naming convention ----

@pytest.mark.parametrize("parser_cls,filename,private_name", [
    (PythonParser, "sample.py", "_private_method"),
    (JavaScriptParser, "sample.js", "_privateMethod"),
    (TypeScriptParser, "sample.ts", "_privateMethod"),
])
def test_private_method_flagged(parser_cls, filename, private_name):
    parsed = _parse(parser_cls, filename)
    my_class = next(c for c in parsed.classes if c.name == "MyClass")
    method = next(m for m in my_class.methods if m.name == private_name)
    assert method.is_private is True


# ---- entry point detection ----

@pytest.mark.parametrize("parser_cls,filename", [
    (PythonParser, "sample.py"),
    (JavaScriptParser, "sample.js"),
    (TypeScriptParser, "sample.ts"),
])
def test_entry_point_detected(parser_cls, filename):
    parsed = _parse(parser_cls, filename)
    assert parsed.has_entry_point is True


# ---- TypeScript-specific: typed + optional + default params ----

def test_ts_typed_params():
    parsed = _parse(TypeScriptParser, "sample.ts")
    greet = next(f for f in parsed.functions if f.name == "greet")
    by_name = {p.name: p for p in greet.params}

    assert by_name["name"].type_hint == "string"
    assert by_name["title"].type_hint == "string", "optional_parameter type_hint not extracted"
    assert by_name["punctuation"].default_value is not None, "default-valued typed param missed"


# ---- import extraction: ES6 + CommonJS both captured (JS/TS) ----

@pytest.mark.parametrize("parser_cls,filename", [
    (JavaScriptParser, "sample.js"),
    (TypeScriptParser, "sample.ts"),
])
def test_both_import_styles_captured(parser_cls, filename):
    parsed = _parse(parser_cls, filename)
    modules = {i.module for i in parsed.imports}
    assert "fs" in modules, "ES6 import not captured"
    assert "path" in modules, "CommonJS require() not captured"


# ---- graceful failure on syntax errors: no crash, warning logged ----

@pytest.mark.parametrize("parser_cls,filename,broken_source", [
    (JavaScriptParser, "broken.js", "class Foo { \n  method(x) {\n    return x\n"),  # unclosed braces
    (TypeScriptParser, "broken.ts", "function f(x: number\n  return x;\n"),  # unclosed paren
])
def test_syntax_error_does_not_crash_and_logs_warning(tmp_path, caplog, parser_cls, filename, broken_source):
    broken_file = tmp_path / filename
    broken_file.write_text(broken_source, encoding="utf-8")

    parser = parser_cls(project_root=str(tmp_path))
    with caplog.at_level(logging.WARNING):
        result = parser.parse_file(filename)

    assert result is not None, "parser should return a partial result, not None, on recoverable syntax errors"
    assert any("syntax error" in r.message.lower() for r in caplog.records), (
        "expected a warning log entry mentioning syntax errors; none was emitted - "
        "silent partial failure is worse than a crash for a docs tool"
    )