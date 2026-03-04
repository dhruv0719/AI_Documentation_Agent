# models/dependency_graph.py

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
    
    # Depth in the dependency tree (entry points = 0)
    depth: int = 0

@dataclass
class DependencyGraph:
    """Graph of module dependencies in the project."""
    
    nodes: Dict[str, ModuleNode] = field(default_factory=dict)
    
    # Files that are entry points (have if __name__ == "__main__")
    entry_points: List[str] = field(default_factory=list)
    
    # Files that nothing imports (leaf nodes)
    leaf_modules: List[str] = field(default_factory=list)
    
    # Files that import nothing (root/external facing)
    root_modules: List[str] = field(default_factory=list)
    
    # Circular dependencies detected
    circular_dependencies: List[List[str]] = field(default_factory=list)
    
    def add_module(self, file_path: str, module_name: str, imports: List[str]):
        """Add a module to the graph."""
        self.nodes[file_path] = ModuleNode(
            file_path=file_path,
            module_name=module_name,
            imports=imports
        )
    
    def build_reverse_dependencies(self):
        """After all modules added, build imported_by relationships."""
        for file_path, node in self.nodes.items():
            for imp in node.imports:
                # Find which module this import refers to
                for other_path, other_node in self.nodes.items():
                    if other_node.module_name == imp or other_path.endswith(f"{imp}.py"):
                        other_node.imported_by.append(file_path)
    
    def find_entry_points(self):
        """Identify entry point modules."""
        # Entry points: files with if __name__ == "__main__"
        # This should be detected during parsing
        pass
    
    def calculate_depths(self):
        """Calculate depth of each module from entry points."""
        # BFS from entry points
        visited = set()
        queue = [(ep, 0) for ep in self.entry_points]
        
        while queue:
            file_path, depth = queue.pop(0)
            if file_path in visited:
                continue
            visited.add(file_path)
            
            if file_path in self.nodes:
                self.nodes[file_path].depth = depth
                for imp in self.nodes[file_path].imports:
                    # Find the actual file for this import
                    for other_path in self.nodes:
                        if other_path.endswith(f"{imp}.py"):
                            queue.append((other_path, depth + 1))
    
    def get_analysis_order(self) -> List[str]:
        """Get files in order they should be analyzed (leaves first)."""
        # Sort by depth descending (deepest dependencies first)
        sorted_nodes = sorted(
            self.nodes.values(),
            key=lambda n: n.depth,
            reverse=True
        )
        return [n.file_path for n in sorted_nodes]
    
    def to_mermaid(self) -> str:
        """Generate Mermaid diagram of dependencies."""
        lines = ["graph TD"]
        for file_path, node in self.nodes.items():
            safe_name = node.module_name.replace(".", "_")
            for imp in node.imports:
                safe_imp = imp.replace(".", "_")
                lines.append(f"    {safe_name} --> {safe_imp}")
        return "\n".join(lines)