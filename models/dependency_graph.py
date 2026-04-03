# models/dependency_graph.py
"""Data models for module dependency analysis."""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional

@dataclass
class ModuleNode:
    """Represents a module in the dependency graph."""
    file_path: str
    module_name: str
    
    # What this module imports
    imports: List[str] = field(default_factory=list)
    
    # What modules import this one (reverse dependencies)
    imported_by: List[str] = field(default_factory=list)

    # External dependencies (pip packages)
    external_deps: List[str] = field(default_factory=list)
    
    # Depth from entry point (0 = entry point, 1 = imported by entry, etc.)
    depth: int = -1  # -1 means not calculated

    @property
    def is_leaf(self) -> bool:
        """True if nothing imports this module."""
        return len(self.imported_by) == 0
    
    @property
    def is_root(self) -> bool:
        """True if this module doesn't import any internal modules."""
        return len(self.imports) == 0
    
    @property
    def coupling_score(self) -> int:
        """How coupled this module is (total connections)."""
        return len(self.imports) + len(self.imported_by)
    
@dataclass
class CircularDependency:
    """Represents a circular dependency cycle."""
    cycle: List[str]  # File paths forming the cycle

    @property
    def length(self) -> int:
        """Number of modules in the cycle"""
        return len(self.cycle)
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return " → ".join(self.cycle)

@dataclass
class DependencyGraph:
    """
    Graph of module dependencies.
    
    This is a DATA model. All graph-building logic
    lives in DependencyAnalyzer.
    """
    
    nodes: Dict[str, ModuleNode] = field(default_factory=dict)
    
    # Files that are entry points (have if __name__ == "__main__")
    entry_points: List[str] = field(default_factory=list)
    
    # Circular dependencies detected
    circular_dependencies: List[CircularDependency] = field(default_factory=list)

    @property
    def total_modules(self) -> int:
        """Total number of modules in the project."""
        return len(self.nodes)

    @property
    def root_modules(self) -> List[str]:
        """Modules that don't import any internal modules (utility modules)."""
        return [p for p, n in self.nodes.items() if n.is_root]
    
    @property
    def leaf_modules(self) -> List[str]:
        """Modules that nothing else imports (dead code candidates)."""
        return [p for p, n in self.nodes.items() if n.is_leaf]
    
    @property
    def most_imported(self) -> List[tuple]:
        """
        Modules sorted by how many other modules import them.
        
        Returns:
            List of (file_path, import_count) tuples, sorted by count descending
        """
        return sorted(
            [(p, len(n.imported_by)) for p, n in self.nodes.items()],
            key=lambda x: x[1],
            reverse=True
        )
    
    @property
    def most_coupled(self) -> List[tuple]:
        """
        Modules with highest coupling (most connections).
        
        Returns:
            List of (file_path, coupling_score) tuples
        """
        return sorted(
            [(path, node.coupling_score) for path, node in self.nodes.items()],
            key=lambda x: x[1],
            reverse=True
        )
    
    @property
    def has_circular_dependencies(self) -> bool:
        """True if circular dependencies were detected."""
        return len(self.circular_dependencies) > 0

    def get_node(self, file_path: str) -> Optional[ModuleNode]:
        """Get a module node by file path."""
        return self.nodes.get(file_path)
    
    def get_dependencies(self, file_path: str) -> List[str]:
        """Get all modules that the given file imports."""
        node = self.nodes.get(file_path)
        return node.imports if node else []
    
    def get_dependents(self, file_path: str) -> List[str]:
        """Get all modules that import the given file."""
        node = self.nodes.get(file_path)
        return node.imported_by if node else []
    
    # def add_module(self, file_path: str, module_name: str, imports: List[str]):
    #     """Add a module to the graph."""
    #     self.nodes[file_path] = ModuleNode(
    #         file_path=file_path,
    #         module_name=module_name,
    #         imports=imports
    #     )
    
    # def build_reverse_dependencies(self):
    #     """After all modules added, build imported_by relationships."""
    #     for file_path, node in self.nodes.items():
    #         for imp in node.imports:
    #             # Find which module this import refers to
    #             for other_path, other_node in self.nodes.items():
    #                 if other_node.module_name == imp or other_path.endswith(f"{imp}.py"):
    #                     other_node.imported_by.append(file_path)
    
    # def find_entry_points(self):
    #     """Identify entry point modules."""
    #     # Entry points: files with if __name__ == "__main__"
    #     # This should be detected during parsing
    #     pass
    
    # def calculate_depths(self):
    #     """Calculate depth of each module from entry points."""
    #     # BFS from entry points
    #     visited = set()
    #     queue = [(ep, 0) for ep in self.entry_points]
        
    #     while queue:
    #         file_path, depth = queue.pop(0)
    #         if file_path in visited:
    #             continue
    #         visited.add(file_path)
            
    #         if file_path in self.nodes:
    #             self.nodes[file_path].depth = depth
    #             for imp in self.nodes[file_path].imports:
    #                 # Find the actual file for this import
    #                 for other_path in self.nodes:
    #                     if other_path.endswith(f"{imp}.py"):
    #                         queue.append((other_path, depth + 1))
    
    # def get_analysis_order(self) -> List[str]:
    #     """
    #     Get optimal order for analyzing files.
        
    #     Strategy: Analyze dependencies before dependents (topological sort).
    #     This way, when we analyze a file, we already understand what it depends on.
        
    #     Returns:
    #         List of file paths in optimal analysis order
    #     """
    #     result = []
    #     visited = set()
        
    #     def visit(path: str):
    #         if path in visited or path not in self.nodes:
    #             return
    #         visited.add(path)
            
    #         # Visit dependencies first
    #         for imp in self.nodes[path].imports:
    #             visit(imp)
            
    #         result.append(path)
        
    #     # Start from entry points
    #     for entry in self.entry_points:
    #         visit(entry)
        
    #     # Then visit any remaining nodes
    #     for path in self.nodes:
    #         visit(path)
        
    #     return result
    
    # def to_mermaid(self) -> str:
    #     """Generate Mermaid diagram of dependencies."""
    #     lines = ["graph TD"]
    #     for file_path, node in self.nodes.items():
    #         safe_name = node.module_name.replace(".", "_")
    #         for imp in node.imports:
    #             safe_imp = imp.replace(".", "_")
    #             lines.append(f"    {safe_name} --> {safe_imp}")
    #     return "\n".join(lines)

    def get_analysis_order(self) -> List[str]:
        """
        Get optimal analysis order (topological sort).
        
        Analyze dependencies before dependents so when we
        analyze a file, we already understand what it depends on.
        """
        result = []
        visited = set()
        
        def visit(path: str):
            if path in visited or path not in self.nodes:
                return
            visited.add(path)
            
            for imp in self.nodes[path].imports:
                visit(imp)
            
            result.append(path)
        
        # Start from entry points
        for entry in self.entry_points:
            visit(entry)
        
        # Then visit remaining
        for path in self.nodes:
            visit(path)
        
        return result
    
    def get_external_dependencies(self) -> List[str]:
        """Get all unique external dependencies across the project."""
        all_external = set()
        for node in self.nodes.values():
            all_external.update(node.external_deps)
        return sorted(all_external)
    
    def get_modules_at_depth(self, depth: int) -> List[str]:
        """Get all modules at a specific depth from entry points."""
        return [
            path for path, node in self.nodes.items()
            if node.depth == depth
        ]