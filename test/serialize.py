# test/serialize.py
"""Deterministic dict serialization of ParsedFile for snapshot comparison.

line_number is intentionally excluded from snapshots: it's real and useful in
production, but makes fixtures brittle to add/remove a blank line, and adds noise
without protecting against the bugs this suite exists to catch (wrong field
mappings, missed node types, leaked docstrings). Structural correctness is
what these tests protect - not exact line accounting.
"""


def serialize_param(p):
    return {"name": p.name, "type_hint": p.type_hint, "default_value": p.default_value}


def serialize_function(f):
    return {
        "name": f.name,
        "params": [serialize_param(p) for p in f.params],
        "returns": f.returns,
        "docstring": f.docstring,
        "decorators": sorted(f.decorators),
        "is_async": f.is_async,
        "is_private": f.is_private,
    }


def serialize_class(c):
    return {
        "name": c.name,
        "docstring": c.docstring,
        "base_classes": sorted(c.base_classes),
        "decorators": sorted(c.decorators),
        "class_variables": sorted(c.class_variables),
        "methods": {m.name: serialize_function(m) for m in c.methods},
    }


def serialize_import(i):
    return {
        "module": i.module,
        "alias": i.alias,
        "names": sorted(i.names) if i.names else [],
        "is_from_import": i.is_from_import,
    }


def serialize_parsed_file(pf):
    return {
        "module_docstring": pf.module_docstring,
        "has_entry_point": pf.has_entry_point,
        "imports": sorted([serialize_import(i) for i in pf.imports], key=lambda x: x["module"]),
        "classes": {c.name: serialize_class(c) for c in pf.classes},
        "functions": {f.name: serialize_function(f) for f in pf.functions},
        "global_variables": sorted(pf.global_variables),
    }