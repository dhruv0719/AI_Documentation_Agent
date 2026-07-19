# analysis/dependency_analyzer.py
"""Builds a graph of how modules import each other."""

import posixpath
from pathlib import Path
from typing import List, Dict, Optional
from collections import deque
from models.parsed_file import ParsedFile
from models.dependency_graph import DependencyGraph, ModuleNode, CircularDependency

# Extensions/index-file patterns tried when resolving a relative JS/TS import
# ('./utils' -> utils.js, utils.ts, utils/index.js, ...), mirroring Node's
# module resolution algorithm closely enough for a docs tool's purposes.
_RELATIVE_IMPORT_EXTENSIONS = ('.js', '.jsx', '.ts', '.tsx')


class DependencyAnalyzer:
    """Analyzes dependencies between project modules."""

    def __init__(self, project_root: str, parsed_files: List[ParsedFile]):
        self.project_root = Path(project_root)
        self.parsed_files = parsed_files

        self.module_to_path: Dict[str, str] = {}
        self._build_module_mapping()

        # posix-normalized file_path -> original file_path, for relative-import
        # resolution (JS/TS). Built once so resolution is O(1) per candidate
        # instead of re-scanning parsed_files for every import.
        self._posix_path_to_original: Dict[str, str] = {
            Path(pf.file_path).as_posix(): pf.file_path for pf in self.parsed_files
        }

    def build_graph(self) -> DependencyGraph:
        graph = DependencyGraph()
        self._create_nodes(graph)
        self._build_reverse_dependencies(graph)
        self._calculate_depths(graph)
        self._detect_cycles(graph)
        return graph

    # ============================================================
    # GRAPH BUILDING (Private)
    # ============================================================

    def _create_nodes(self, graph: DependencyGraph):
        for pf in self.parsed_files:
            is_entry = self._is_entry_point(pf)

            internal_imports = []
            external_deps = []

            for imp in pf.imports:
                imp_name = self._extract_import_name(imp)

                if imp_name.startswith('.'):
                    # Relative import ('./utils', '../lib/foo') - JS/TS style.
                    # Python's `from .utils import x` produces module="utils"
                    # (ast strips leading dots into node.level separately), so
                    # this branch only ever fires for JS/TS-style imports.
                    resolved = self._resolve_relative_import(pf.file_path, imp_name)
                    if resolved:
                        internal_imports.append(resolved)
                    else:
                        # Couldn't resolve (e.g. points outside scanned files) -
                        # still record it so it's visible, just not linked.
                        external_deps.append(imp_name)
                elif self._is_internal_import(imp_name):
                    resolved = self._resolve_import(imp_name)
                    if resolved:
                        internal_imports.append(resolved)
                    else:
                        external_deps.append(imp_name)
                else:
                    external_deps.append(imp_name)

            node = ModuleNode(
                file_path=pf.file_path,
                module_name=Path(pf.file_path).stem,
                imports=internal_imports,
                external_deps=external_deps
            )
            graph.nodes[pf.file_path] = node

            if is_entry:
                graph.entry_points.append(pf.file_path)

    def _build_reverse_dependencies(self, graph: DependencyGraph):
        for path, node in graph.nodes.items():
            for imp in node.imports:
                if imp in graph.nodes:
                    if path not in graph.nodes[imp].imported_by:
                        graph.nodes[imp].imported_by.append(path)

    def _calculate_depths(self, graph: DependencyGraph):
        queue = deque()
        for entry in graph.entry_points:
            if entry in graph.nodes:
                graph.nodes[entry].depth = 0
                queue.append(entry)
        while queue:
            current = queue.popleft()
            current_depth = graph.nodes[current].depth
            for imp in graph.nodes[current].imports:
                if imp in graph.nodes:
                    node = graph.nodes[imp]
                    new_depth = current_depth + 1
                    if node.depth == -1 or node.depth > new_depth:
                        node.depth = new_depth
                        queue.append(imp)

    def _detect_cycles(self, graph: DependencyGraph):
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {path: WHITE for path in graph.nodes}
        cycles = []

        def dfs(path: str, stack: List[str]):
            colors[path] = GRAY
            stack.append(path)
            node = graph.nodes[path]
            for imp in node.imports:
                if imp not in graph.nodes:
                    continue
                if colors[imp] == GRAY:
                    cycle_start = stack.index(imp)
                    cycle_path = stack[cycle_start:] + [imp]
                    cycles.append(CircularDependency(cycle=cycle_path))
                elif colors[imp] == WHITE:
                    dfs(imp, stack)
            stack.pop()
            colors[path] = BLACK

        for path in graph.nodes:
            if colors[path] == WHITE:
                dfs(path, [])

        graph.circular_dependencies = cycles

    # ============================================================
    # MODULE RESOLUTION (Private)
    # ============================================================

    def _build_module_mapping(self):
        """Python-style dotted-module resolution (unchanged) - used for
        non-relative imports (e.g. `import core.scanner`, `from core import x`)."""
        for pf in self.parsed_files:
            path = Path(pf.file_path)
            simple_name = path.stem
            self.module_to_path[simple_name] = pf.file_path
            parts = list(path.parts)
            if parts[-1].endswith('.py'):
                parts[-1] = parts[-1][:-3]
            dotted_name = '.'.join(parts)
            self.module_to_path[dotted_name] = pf.file_path

    def _extract_import_name(self, imp) -> str:
        if hasattr(imp, 'module'):
            return imp.module
        return str(imp)

    def _is_entry_point(self, parsed_file: ParsedFile) -> bool:
        if hasattr(parsed_file, 'has_entry_point'):
            return parsed_file.has_entry_point
        name = Path(parsed_file.file_path).stem
        return name in ['main', 'app', 'cli', 'run', '__main__']

    def _is_internal_import(self, import_name: str) -> bool:
        """Python-style dotted-module internal check (unchanged). Relative
        JS/TS imports never reach this - they're intercepted in _create_nodes
        before this is called."""
        for module_name in self.module_to_path:
            if import_name == module_name or import_name.startswith(module_name + '.'):
                return True
        first_part = import_name.split('.')[0]
        for pf in self.parsed_files:
            if pf.file_path.startswith(first_part + '/') or pf.file_path.startswith(first_part + '\\'):
                return True
        return False

    def _resolve_import(self, import_name: str) -> Optional[str]:
        if import_name in self.module_to_path:
            return self.module_to_path[import_name]
        parts = import_name.split('.')
        for i in range(len(parts), 0, -1):
            partial = '.'.join(parts[:i])
            if partial in self.module_to_path:
                return self.module_to_path[partial]
        return None

    def _resolve_relative_import(self, importing_file: str, import_name: str) -> Optional[str]:
        """Resolve a JS/TS-style relative import ('./utils', '../lib/foo')
        against the actual scanned files, relative to the IMPORTING file's
        directory (not the project root - relative imports are always
        relative to the file that contains them).

        Tries, in order: exact match (import already has an extension),
        each known extension appended, then each extension as an index file
        inside a directory of that name - mirroring Node's resolution order
        closely enough for dependency-graph purposes.
        """
        importing_dir = Path(importing_file).parent
        joined = (importing_dir / import_name).as_posix()
        normalized = posixpath.normpath(joined)

        candidates = [normalized]
        candidates += [f"{normalized}{ext}" for ext in _RELATIVE_IMPORT_EXTENSIONS]
        candidates += [f"{normalized}/index{ext}" for ext in _RELATIVE_IMPORT_EXTENSIONS]

        for candidate in candidates:
            original = self._posix_path_to_original.get(candidate)
            if original:
                return original
        return None

    # ============================================================
    # OUTPUT GENERATION (Public) - unchanged from original
    # ============================================================

    def generate_summary(self, graph: DependencyGraph) -> str:
        lines = [
            "DEPENDENCY ANALYSIS", "=" * 60,
            f"Total modules: {graph.total_modules}",
            f"Entry points: {len(graph.entry_points)}",
            f"Circular dependencies: {len(graph.circular_dependencies)}",
            "", "Entry Points:",
        ]
        for ep in graph.entry_points:
            lines.append(f"  • {ep}")
        lines.extend(["", "Most Imported Modules:"])
        for path, count in graph.most_imported[:5]:
            if count > 0:
                lines.append(f"  • {Path(path).stem}: imported by {count} modules")
        if graph.has_circular_dependencies:
            lines.extend(["", "⚠️  Circular Dependencies Detected:"])
            for cycle in graph.circular_dependencies:
                lines.append(f"  • {cycle}")
        return "\n".join(lines)

    def generate_mermaid(self, graph: DependencyGraph, max_nodes: int = 50) -> str:
        lines = ["graph TD"]
        if len(graph.nodes) > max_nodes:
            important_paths = [path for path, _ in graph.most_imported[:max_nodes]]
            nodes_to_include = set(important_paths)
        else:
            nodes_to_include = set(graph.nodes.keys())
        for path in nodes_to_include:
            node = graph.nodes[path]
            safe_name = self._sanitize_for_mermaid(node.module_name)
            for imp in node.imports:
                if imp in nodes_to_include:
                    safe_imp = self._sanitize_for_mermaid(graph.nodes[imp].module_name)
                    lines.append(f"    {safe_name} --> {safe_imp}")
        return "\n".join(lines)

    def _sanitize_for_mermaid(self, name: str) -> str:
        return name.replace(".", "_").replace("-", "_").replace(" ", "_")