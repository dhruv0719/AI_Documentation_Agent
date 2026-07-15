"""Verifies two open questions against the real installed grammars:

1. Does tree-sitter-typescript expose a distinct 'optional_parameter' node
   type for `param?: string`, with the same pattern/type fields as
   required_parameter? Confirms whether the parser's existing branch
   already handles it, or silently skips it.

2. Does _attach_leading_docstring leak a docstring across two back-to-back
   class declarations with no comment between them? (i.e. does the second
   class incorrectly inherit the first class's trailing JSDoc, or does it
   correctly report no docstring?)
"""

from tree_sitter import Parser, Language
from tree_sitter_javascript import language as javascript_language
from tree_sitter_typescript import language_typescript

# ---------------------------------------------------------------------
# TEST 1: optional_parameter node type
# ---------------------------------------------------------------------
ts_parser = Parser()
ts_parser.language = Language(language_typescript())

optional_param_sample = b"""
function greet(name: string, title?: string) {
    return name;
}
"""

tree = ts_parser.parse(optional_param_sample)
root = tree.root_node

print("=" * 70)
print("TEST 1: optional_parameter node type")
print("=" * 70)

for node in root.children:
    if node.type == "function_declaration":
        params_node = node.child_by_field_name("parameters")
        for p in params_node.named_children:
            fields = []
            for i in range(p.child_count):
                fname = p.field_name_for_child(i)
                if fname:
                    fields.append(f"{fname}->{p.child(i).type}")
            text = optional_param_sample[p.start_byte:p.end_byte].decode()
            print(f"  node.type={p.type!r}  fields={fields}  text={text!r}")

print()
print("Import the actual parser's _extract_params and run it directly:")
import sys
sys.path.insert(0, "/home/claude/test_proj")
from parsers.typescript_parser import _extract_params

for node in root.children:
    if node.type == "function_declaration":
        params_node = node.child_by_field_name("parameters")
        result = _extract_params(params_node, optional_param_sample)
        print(f"  _extract_params() result: {[(p.name, p.type_hint) for p in result]}")
        print(f"  Expected 2 params (name, title) - got {len(result)}")


# ---------------------------------------------------------------------
# TEST 2: back-to-back classes, docstring leak check
# ---------------------------------------------------------------------
js_parser = Parser()
js_parser.language = Language(javascript_language())

leak_sample = b"""
/** Documented class */
class First {}
class Second {}
class Third extends Second {}
"""

tree2 = js_parser.parse(leak_sample)
root2 = tree2.root_node

print()
print("=" * 70)
print("TEST 2: docstring leak on back-to-back classes")
print("=" * 70)

from parsers.javascript_parser import _attach_leading_docstring

for node in root2.children:
    if node.type == "class_declaration":
        name_node = node.child_by_field_name("name")
        name = leak_sample[name_node.start_byte:name_node.end_byte].decode()
        doc = _attach_leading_docstring(node, leak_sample)
        prev_sibling_type = node.prev_sibling.type if node.prev_sibling else None
        print(f"  class {name}: docstring={doc!r}  (prev_sibling.type={prev_sibling_type!r})")

print()
print("Expected: First='Documented class', Second=None, Third=None")
print("If Second or Third show a docstring, that's a leak.")