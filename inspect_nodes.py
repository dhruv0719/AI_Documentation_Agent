"""Inspect tree-sitter node types and field names for JS sample code.
Prints the raw tree structure so we can confirm exact field names
before trusting the extraction logic in javascript_parser.py.
"""

from tree_sitter import Parser, Language
from tree_sitter_javascript import language as javascript_language

parser = Parser()
parser.language = Language(javascript_language())

sample = b"""
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

tree = parser.parse(sample)
root = tree.root_node


def dump(node, source, depth=0, max_depth=6):
    if depth > max_depth:
        return
    text_preview = source[node.start_byte:node.end_byte].decode("utf-8")
    text_preview = text_preview.replace("\n", "\\n")[:40]
    print("  " * depth + f"{node.type!r} fields={_field_names(node)} text={text_preview!r}")
    for child in node.children:
        dump(child, source, depth + 1, max_depth)


def _field_names(node):
    """Show which field name (if any) each child is registered under."""
    names = []
    for i in range(node.child_count):
        child = node.child(i)
        fname = node.field_name_for_child(i)
        if fname:
            names.append(f"{fname}->{child.type}")
    return names


print("=" * 70)
print("FULL TREE DUMP (type, field-name mapping, text preview)")
print("=" * 70)
dump(root, sample)

print()
print("=" * 70)
print("FOCUSED CHECKS")
print("=" * 70)

# Find class_declaration for MyClass and inspect its fields directly
for node in root.children:
    if node.type == "class_declaration":
        name_node = node.child_by_field_name("name")
        name = sample[name_node.start_byte:name_node.end_byte].decode() if name_node else "?"
        print(f"\nclass_declaration: {name}")
        print(f"  child_by_field_name('superclass') -> {node.child_by_field_name('superclass')}")
        print(f"  child_by_field_name('heritage') -> {node.child_by_field_name('heritage')}")
        for child in node.children:
            print(f"  child: type={child.type!r}")
            if child.type == "class_heritage":
                for gc in child.children:
                    print(f"    grandchild: type={gc.type!r} text={sample[gc.start_byte:gc.end_byte].decode()!r}")

        body = node.child_by_field_name("body")
        if body:
            for child in body.children:
                if child.type in ("method_definition", "field_definition", "public_field_definition"):
                    print(f"\n  member: type={child.type!r}")
                    for i in range(child.child_count):
                        c = child.child(i)
                        fname = child.field_name_for_child(i)
                        ctext = sample[c.start_byte:c.end_byte].decode().replace("\n", "\\n")[:30]
                        print(f"    idx={i} field={fname!r} type={c.type!r} text={ctext!r}")
                    print(f"    child_by_field_name('name') -> {child.child_by_field_name('name')}")
                    print(f"    child_by_field_name('property') -> {child.child_by_field_name('property')}")
                    print(f"    child_by_field_name('async_modifier') -> {child.child_by_field_name('async_modifier')}")