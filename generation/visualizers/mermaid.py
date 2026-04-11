# generation/visualizers/mermaid.py
"""
Mermaid Diagram Generator

Generates Mermaid.js diagrams for:
- Module dependencies
- Class hierarchies
- Project architecture
"""

from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass

# Import your models (adjust paths as needed)
try:
    from models.parsed_file import ParsedFile, ClassInfo
except ImportError:
    ParsedFile = None
    ClassInfo = None


class MermaidGenerator:
    """
    Generates Mermaid diagram code.
    
    Mermaid diagrams can be rendered in:
    - GitHub markdown (automatic)
    - GitLab markdown (automatic)
    - VS Code with extension
    - https://mermaid.live
    
    Usage:
        generator = MermaidGenerator()
        diagram = generator.dependency_diagram(parsed_files)
        
        # Include in markdown:
        # ```mermaid
        # {diagram}
        # ```
    """
    
    def __init__(self):
        self.node_counter = 0
    
    def class_diagram(
        self,
        classes: List,  # List[ClassInfo]
        title: str = "Class Diagram"
    ) -> str:
        """
        Generate class relationship diagram.
        
        Args:
            classes: List of ClassInfo objects
            title: Diagram title
        
        Returns:
            Mermaid class diagram code
        """
        lines = ["classDiagram"]
        
        for cls in classes:
            class_name = cls.name
            
            # Add class definition
            lines.append(f"    class {class_name} {{")
            
            # Add methods
            for method in cls.methods[:5]:  # Limit to 5 methods
                visibility = "-" if hasattr(method, 'is_private') and method.is_private else "+"
                params = "..."
                returns = method.returns if method.returns else "None"
                lines.append(f"        {visibility}{method.name}({params}) {returns}")
            
            lines.append("    }")
            
            # Add inheritance
            if hasattr(cls, 'base_classes') and cls.base_classes:
                for base in cls.base_classes:
                    # Skip common bases
                    if base not in ('object', 'ABC'):
                        lines.append(f"    {base} <|-- {class_name}")
        
        return "\n".join(lines)
    
    def flowchart(
        self,
        steps: List[Dict],
        title: str = "Flow"
    ) -> str:
        """
        Generate a flowchart.
        
        Args:
            steps: List of dicts with 'id', 'label', 'next' keys
            title: Diagram title
        
        Returns:
            Mermaid flowchart code
        """
        lines = ["graph TD"]
        
        # Add nodes
        for step in steps:
            node_id = self._safe_id(step.get('id', str(self.node_counter)))
            label = step.get('label', node_id)
            shape = step.get('shape', 'rect')
            
            if shape == 'diamond':
                lines.append(f"    {node_id}{{{label}}}")
            elif shape == 'rounded':
                lines.append(f"    {node_id}({label})")
            elif shape == 'circle':
                lines.append(f"    {node_id}(({label}))")
            else:
                lines.append(f"    {node_id}[{label}]")
            
            self.node_counter += 1
        
        # Add edges
        for step in steps:
            node_id = self._safe_id(step.get('id', ''))
            next_nodes = step.get('next', [])
            
            if isinstance(next_nodes, str):
                next_nodes = [next_nodes]
            
            for next_id in next_nodes:
                safe_next = self._safe_id(next_id)
                edge_label = step.get('edge_label', '')
                
                if edge_label:
                    lines.append(f"    {node_id} -->|{edge_label}| {safe_next}")
                else:
                    lines.append(f"    {node_id} --> {safe_next}")
        
        return "\n".join(lines)
    
    def architecture_diagram(
        self,
        layers: Dict[str, List[str]]
    ) -> str:
        """
        Generate architecture layer diagram.
        
        Args:
            layers: Dict mapping layer names to module names
                    e.g., {"CLI": ["main.py"], "Core": ["scanner.py", "parser.py"]}
        
        Returns:
            Mermaid diagram code
        """
        lines = ["graph TB"]
        
        # Create subgraphs for each layer
        for layer_name, modules in layers.items():
            safe_layer = self._safe_id(layer_name)
            lines.append(f"    subgraph {safe_layer}[{layer_name}]")
            
            for module in modules:
                safe_module = self._safe_id(module.replace('.py', ''))
                lines.append(f"        {safe_module}[{module}]")
            
            lines.append("    end")
        
        # Connect layers (top to bottom)
        layer_names = list(layers.keys())
        for i in range(len(layer_names) - 1):
            current = self._safe_id(layer_names[i])
            next_layer = self._safe_id(layer_names[i + 1])
            lines.append(f"    {current} --> {next_layer}")
        
        return "\n".join(lines)
    
    def _safe_id(self, name: str) -> str:
        """Convert name to safe Mermaid node ID."""
        # Remove special characters, replace spaces
        safe = name.replace(" ", "_").replace("-", "_").replace(".", "_")
        safe = ''.join(c for c in safe if c.isalnum() or c == '_')
        return safe or f"node_{self.node_counter}"
    
    def wrap_for_markdown(self, diagram: str) -> str:
        """Wrap diagram in markdown code fence."""
        return f"```mermaid\n{diagram}\n```"


# Convenience functions
def generate_dependency_diagram(parsed_files: List) -> str:
    """Quick function to generate dependency diagram."""
    return MermaidGenerator().dependency_diagram(parsed_files)


def generate_class_diagram(classes: List) -> str:
    """Quick function to generate class diagram."""
    return MermaidGenerator().class_diagram(classes)


if __name__ == "__main__":
    # Test
    gen = MermaidGenerator()
    
    # Test architecture diagram
    layers = {
        "CLI": ["main.py", "commands.py"],
        "Analysis": ["analyzer.py", "dependency_analyzer.py"],
        "Core": ["scanner.py", "parser.py"],
        "Models": ["parsed_file.py", "metadata.py"]
    }
    
    diagram = gen.architecture_diagram(layers)
    print("Architecture Diagram:")
    print(gen.wrap_for_markdown(diagram))