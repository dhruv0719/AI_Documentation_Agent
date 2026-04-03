# analysis/dependency_analyzer.py
"""Builds a graph of how modules import each other. This help understand Project flow, Module importance, Circular dependencies, Analysis order"""

from pathlib import Path
from typing import List, Dict, Optional
from collections import deque
from models.parsed_file import ParsedFile
from models.dependency_graph import DependencyGraph, ModuleNode, CircularDependency

class DependencyAnalyzer:
    """Analyzes dependencies between project modules."""

    def __init__(self, project_root: str, parsed_files: List[ParsedFile]):
        """
        Initialize dependency analyzer.
        
        Args:
            project_root: Root directory of the project
            parsed_files: List of parsed Python files
        """
        self.project_root = Path(project_root)
        self.parsed_files = parsed_files

        # Build mapping of module names to file paths
        self.module_to_path: Dict[str, str] = {}
        self._build_module_mapping()

    def build_graph(self) -> DependencyGraph:
        """
        Build the complete dependency graph.
        
        Returns:
            DependencyGraph with all modules and relationships
        """
        graph = DependencyGraph()

        # Phase 1: Create nodes for all modules
        self._create_nodes(graph)

        # Phase 2: Build reverse dependencies (imported_by)
        self._build_reverse_dependencies(graph)
        
        # Phase 3: Calculate depths from entry points
        self._calculate_depths(graph)
        
        # Phase 4: Detect circular dependencies
        self._detect_cycles(graph)
        
        return graph
    
    # ============================================================
    # GRAPH BUILDING (Private)
    # ============================================================
    
    def _create_nodes(self, graph: DependencyGraph):
        """Create nodes for all parsed files."""
        for pf in self.parsed_files:
            # Check if this is an entry point
            is_entry = self._is_entry_point(pf)
            
            # Separate internal vs external imports
            internal_imports = []
            external_deps = []
            
            for imp in pf.imports:
                imp_name = self._extract_import_name(imp)
                
                if self._is_internal_import(imp_name):
                    resolved = self._resolve_import(imp_name)
                    if resolved:
                        internal_imports.append(resolved)
                else:
                    external_deps.append(imp_name)
            
            # Create node
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
        """Build imported_by relationships."""
        for path, node in graph.nodes.items():
            for imp in node.imports:
                if imp in graph.nodes:
                    if path not in graph.nodes[imp].imported_by:
                        graph.nodes[imp].imported_by.append(path)
    
    def _calculate_depths(self, graph: DependencyGraph):
        """Calculate depth of each node from entry points using BFS."""
        queue = deque()
        
        # Initialize entry points with depth 0
        for entry in graph.entry_points:
            if entry in graph.nodes:
                graph.nodes[entry].depth = 0
                queue.append(entry)
        
        # BFS to calculate depths
        while queue:
            current = queue.popleft()
            current_depth = graph.nodes[current].depth
            
            for imp in graph.nodes[current].imports:
                if imp in graph.nodes:
                    node = graph.nodes[imp]
                    new_depth = current_depth + 1
                    
                    # Update if not set or found shorter path
                    if node.depth == -1 or node.depth > new_depth:
                        node.depth = new_depth
                        queue.append(imp)
    
    def _detect_cycles(self, graph: DependencyGraph):
        """Detect circular dependencies using DFS."""
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
                    # Found cycle!
                    cycle_start = stack.index(imp)
                    cycle_path = stack[cycle_start:] + [imp]
                    cycles.append(CircularDependency(cycle=cycle_path))
                
                elif colors[imp] == WHITE:
                    dfs(imp, stack)
            
            stack.pop()
            colors[path] = BLACK
        
        # Run DFS from each unvisited node
        for path in graph.nodes:
            if colors[path] == WHITE:
                dfs(path, [])
        
        graph.circular_dependencies = cycles
    
    # ============================================================
    # MODULE RESOLUTION (Private)
    # ============================================================
    
    def _build_module_mapping(self):
        """Build mapping from module names to file paths."""
        for pf in self.parsed_files:
            path = Path(pf.file_path)
            
            # Simple name: utils.py → utils
            simple_name = path.stem
            self.module_to_path[simple_name] = pf.file_path
            
            # Dotted name: core/scanner.py → core.scanner
            parts = list(path.parts)
            if parts[-1].endswith('.py'):
                parts[-1] = parts[-1][:-3]
            dotted_name = '.'.join(parts)
            self.module_to_path[dotted_name] = pf.file_path
    
    def _extract_import_name(self, imp) -> str:
        """Extract import name from ImportInfo object or string."""
        if hasattr(imp, 'module'):
            return imp.module
        return str(imp)
    
    def _is_entry_point(self, parsed_file: ParsedFile) -> bool:
        """Check if file is an entry point."""
        # Check if ParsedFile has entry point flag
        if hasattr(parsed_file, 'has_entry_point'):
            return parsed_file.has_entry_point
        
        # Fallback: check common entry point names
        name = Path(parsed_file.file_path).stem
        return name in ['main', 'app', 'cli', 'run', '__main__']
    
    def _is_internal_import(self, import_name: str) -> bool:
        """Check if import is from within the project."""
        # Check direct module match
        for module_name in self.module_to_path:
            if import_name == module_name or import_name.startswith(module_name + '.'):
                return True
        
        # Check if matches a directory in project
        first_part = import_name.split('.')[0]
        for pf in self.parsed_files:
            if pf.file_path.startswith(first_part + '/') or pf.file_path.startswith(first_part + '\\'):
                return True
        
        return False
    
    def _resolve_import(self, import_name: str) -> Optional[str]:
        """Resolve import name to file path."""
        # Direct match
        if import_name in self.module_to_path:
            return self.module_to_path[import_name]
        
        # Try progressively shorter partial matches
        parts = import_name.split('.')
        for i in range(len(parts), 0, -1):
            partial = '.'.join(parts[:i])
            if partial in self.module_to_path:
                return self.module_to_path[partial]
        
        return None
    
    # ============================================================
    # OUTPUT GENERATION (Public)
    # ============================================================
    
    def generate_summary(self, graph: DependencyGraph) -> str:
        """
        Generate text summary of dependency analysis.
        
        Args:
            graph: DependencyGraph to summarize
            
        Returns:
            Multi-line string with summary
        """
        lines = [
            "DEPENDENCY ANALYSIS",
            "=" * 60,
            f"Total modules: {graph.total_modules}",
            f"Entry points: {len(graph.entry_points)}",
            f"Circular dependencies: {len(graph.circular_dependencies)}",
            "",
            "Entry Points:",
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
        """
        Generate Mermaid diagram syntax.
        
        Args:
            graph: DependencyGraph to visualize
            max_nodes: Maximum nodes to include (prevents huge diagrams)
            
        Returns:
            Mermaid diagram syntax
        """
        lines = ["graph TD"]
        
        # Limit to most important nodes if graph is large
        if len(graph.nodes) > max_nodes:
            important_paths = [path for path, _ in graph.most_imported[:max_nodes]]
            nodes_to_include = set(important_paths)
        else:
            nodes_to_include = set(graph.nodes.keys())
        
        # Generate edges
        for path in nodes_to_include:
            node = graph.nodes[path]
            safe_name = self._sanitize_for_mermaid(node.module_name)
            
            for imp in node.imports:
                if imp in nodes_to_include:
                    safe_imp = self._sanitize_for_mermaid(graph.nodes[imp].module_name)
                    lines.append(f"    {safe_name} --> {safe_imp}")
        
        return "\n".join(lines)
    
    def _sanitize_for_mermaid(self, name: str) -> str:
        """Sanitize module name for Mermaid syntax."""
        return name.replace(".", "_").replace("-", "_").replace(" ", "_")


# ============================================================
# MAIN (for testing)
# ============================================================

if __name__ == "__main__":
    from core.scanner import scan_project
    from parsers.python_parser import parse_file
    
    project_root = r"D:\AI_Documentation_Agent"
    
    print("Scanning project...")
    files = scan_project(project_root, ignore_dirs=["venv", ".venv", "__pycache__"])
    
    print(f"Parsing {len(files)} files...")
    parsed = [parse_file(f, project_root) for f in files]
    parsed = [p for p in parsed if p is not None]
    
    print(f"\nBuilding dependency graph...")
    analyzer = DependencyAnalyzer(project_root, parsed)
    graph = analyzer.build_graph()
    
    # Print summary
    print("\n" + analyzer.generate_summary(graph))
    
    print("\n\nOptimal Analysis Order:")
    for i, path in enumerate(graph.get_analysis_order(), 1):
        print(f"  {i:2d}. {path}")
    
    print("\n\nMermaid Diagram:")
    print(analyzer.generate_mermaid(graph)) 