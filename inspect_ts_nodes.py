"""Inspect tree-sitter-typescript node types and field names."""

from tree_sitter import Parser, Language
from tree_sitter_typescript import language_typescript

parser = Parser()
parser.language = Language(language_typescript())

sample = b"""
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

tree = parser.parse(sample)
root = tree.root_node


def _field_names(node):
    names = []
    for i in range(node.child_count):
        child = node.child(i)
        fname = node.field_name_for_child(i)
        if fname:
            names.append(f"{fname}->{child.type}")
    return names


def dump(node, source, depth=0, max_depth=8):
    if depth > max_depth:
        return
    text_preview = source[node.start_byte:node.end_byte].decode("utf-8")
    text_preview = text_preview.replace("\n", "\\n")[:40]
    print("  " * depth + f"{node.type!r} fields={_field_names(node)} text={text_preview!r}")
    for child in node.children:
        dump(child, source, depth + 1, max_depth)


print("=" * 70)
print("FULL TREE DUMP")
print("=" * 70)
dump(root, sample)

print()
print("=" * 70)
print("FOCUSED: class_declaration heritage + typed params")
print("=" * 70)
for node in root.children:
    if node.type == "class_declaration":
        name_node = node.child_by_field_name("name")
        name = sample[name_node.start_byte:name_node.end_byte].decode() if name_node else "?"
        print(f"\nclass_declaration: {name}")
        for child in node.children:
            print(f"  child: type={child.type!r} field={node.field_name_for_child(list(node.children).index(child))}")
            if child.type in ("class_heritage",):
                for gc in child.children:
                    print(f"    heritage child: type={gc.type!r} text={sample[gc.start_byte:gc.end_byte].decode()!r}")

        body = node.child_by_field_name("body")
        if body:
            for child in body.children:
                if child.type == "method_definition":
                    params_node = child.child_by_field_name("parameters")
                    print(f"\n  method params_node type={params_node.type if params_node else None}")
                    if params_node:
                        for p in params_node.named_children:
                            print(f"    param node: type={p.type!r} fields={_field_names(p)} text={sample[p.start_byte:p.end_byte].decode()!r}")