# generation/enhanced_generator.py
"""
Enhanced Documentation Generator

Generates comprehensive documentation using:
1. ParsedFile - Actual code structure (functions, classes, signatures)
2. ModuleSummary - LLM-generated insights (purpose, responsibilities)
3. ProjectAnalysis - High-level project understanding
4. DependencyGraph - Module relationships (optional)

Output:
- README.md - Overview documentation
- TECHNICAL_DOC.md - Detailed technical reference
- API_REFERENCE.md - Complete API documentation
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from models.generation_result import GenerationResult
from models.parsed_file import ParsedFile, ModuleSummary, ProjectAnalysis, ClassInfo, FunctionInfo


class EnhancedDocumentationGenerator:
    """
    Generates comprehensive markdown documentation.
    
    Unlike the basic generator, this one:
    - Includes actual function signatures and parameters
    - Documents all classes with their methods
    - Generates API reference with full details
    - Adds Table of Contents
    - Includes dependency diagrams (if mermaid available)
    """
    
    def __init__(self, output_dir: str = "docs"):
        """
        Initialize the generator.
        
        Args:
            output_dir: Directory for generated documentation
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_all(
        self,
        project_analysis: ProjectAnalysis,
        module_summaries: List[ModuleSummary],
        parsed_files: List[ParsedFile],
        project_name: str,
        dependency_diagram: Optional[str] = None,
        project_tree: Optional[str] = None
    ) -> GenerationResult:
        """
        Generate all documentation files.
        
        Args:
            project_analysis: High-level project analysis
            module_summaries: LLM-generated module summaries
            parsed_files: Parsed code structure
            project_name: Name of the project
            dependency_diagram: Optional Mermaid diagram string
        
        Returns:
            GenerationResult with paths to generated files
        """
        import time
        start_time = time.time()

        # Create lookup for summaries by file path
        summary_lookup = {s.file_path: s for s in module_summaries}
        
        # Generate each document
        readme_path = self._generate_readme(
            project_analysis, 
            project_name,
            dependency_diagram,
            project_tree
        )
        
        technical_path = self._generate_technical_doc(
            project_analysis,
            module_summaries,
            parsed_files,
            summary_lookup,
            project_name
        )
        
        api_path = self._generate_api_reference(
            parsed_files,
            summary_lookup,
            project_name
        )

         # Calculate stats
        total_classes = sum(len(pf.classes) for pf in parsed_files)
        total_functions = sum(len(pf.functions) for pf in parsed_files)
        generation_time = time.time() - start_time
        
        return GenerationResult(
            readme_path=readme_path,
            technical_doc_path=technical_path,
            api_reference_path=api_path,
            generated_at=datetime.now(),
            files_documented=len(parsed_files),
            total_classes=total_classes,         
            total_functions=total_functions,      
            generation_time_seconds=generation_time  
        )
    
    # ================================================================
    # README GENERATION
    # ================================================================
    
    def _generate_readme(
        self,
        project_analysis: ProjectAnalysis,
        project_name: str,
        dependency_diagram: Optional[str] = None,
        project_tree: Optional[str] = None
    ) -> Path:
        """Generate README.md"""
        
        lines = [
            f"# {project_name}",
            "",
            f"> 📚 Auto-generated documentation | {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "## 📋 Table of Contents",
            "",
            "- [Overview](#overview)",
            "- [Architecture](#architecture)",
            "- [Entry Points](#entry-points)",
            "- [Module Relationships](#module-relationships)",
            "- [Design Patterns](#design-patterns)",
            "- [Getting Started](#getting-started)",
            "",
            "---",
            "",
            "## Overview",
            "",
            project_analysis.project_purpose,
            "",
            "## Architecture",
            "",
            project_analysis.architecture_overview,
            "",
        ]
        
        # Add dependency diagram if available
        if dependency_diagram:
            lines.extend([
                "### Module Dependencies",
                "",
                "```mermaid",
                dependency_diagram,
                "```",
                "",
            ])
        
        # Entry points
        lines.extend([
            "## Entry Points",
            "",
            "The following files can be executed directly:",
            "",
        ])
        
        for entry in project_analysis.entry_points:
            lines.append(f"- `{entry}`")
        
        lines.append("")
        
        # Module relationships
        lines.extend([
            "## Module Relationships",
            "",
            project_analysis.module_relationships,
            "",
        ])
        
        # Design patterns
        lines.extend([
            "## Design Patterns",
            "",
        ])

        if project_tree:
            lines.extend([
                "## Project Structure",
                "",
                "```",
                project_tree,
                "```",
                "",
            ])
        
        if project_analysis.design_patterns:
            for pattern in project_analysis.design_patterns:
                lines.append(f"- **{pattern}**")
        else:
            lines.append("_No specific patterns identified._")
        
        lines.append("")
        
        # Getting started
        lines.extend([
            "## Getting Started",
            "",
            "### Prerequisites",
            "",
            "```bash",
            "python >= 3.10",
            "```",
            "",
            "### Installation",
            "",
            "```bash",
            "# Clone the repository",
            f"git clone <repository-url>",
            f"cd {project_name.lower().replace(' ', '-')}",
            "",
            "# Install dependencies",
            "pip install -r requirements.txt",
            "```",
            "",
            "### Usage",
            "",
            "```bash",
        ])
        
        # Add entry point commands
        for entry in project_analysis.entry_points[:1]:
            lines.append(f"python {entry}")
        
        lines.extend([
            "```",
            "",
            "---",
            "",
            "_This documentation was auto-generated by Code Documentation Agent._",
        ])
        
        # Write file
        readme_path = self.output_dir / "README.md"
        readme_path.write_text("\n".join(lines), encoding="utf-8")
        
        return readme_path
    
    # ================================================================
    # TECHNICAL DOCUMENTATION
    # ================================================================
    
    def _generate_technical_doc(
        self,
        project_analysis: ProjectAnalysis,
        module_summaries: List[ModuleSummary],
        parsed_files: List[ParsedFile],
        summary_lookup: Dict[str, ModuleSummary],
        project_name: str
    ) -> Path:
        """Generate TECHNICAL_DOC.md"""
        
        lines = [
            f"# {project_name} - Technical Documentation",
            "",
            f"> 🔧 Developer Reference | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 📋 Table of Contents",
            "",
            "- [Architecture Overview](#architecture-overview)",
            "- [Design Patterns](#design-patterns)",
            "- [Module Reference](#module-reference)",
        ]
        
        # Add module links to TOC
        sorted_files = sorted(parsed_files, key=lambda x: x.file_path)
        for pf in sorted_files:
            module_name = Path(pf.file_path).stem
            anchor = module_name.lower().replace("_", "-")
            lines.append(f"  - [{pf.file_path}](#{anchor})")
        
        lines.extend([
            "",
            "---",
            "",
            "## Architecture Overview",
            "",
            project_analysis.architecture_overview,
            "",
            "### Module Relationships",
            "",
            project_analysis.module_relationships,
            "",
            "## Design Patterns",
            "",
        ])
        
        if project_analysis.design_patterns:
            for pattern in project_analysis.design_patterns:
                lines.append(f"- **{pattern}**")
        else:
            lines.append("_No specific patterns identified._")
        
        lines.extend([
            "",
            "---",
            "",
            "## Module Reference",
            "",
        ])
        
        # Generate detailed documentation for each module
        for pf in sorted_files:
            summary = summary_lookup.get(pf.file_path)
            lines.extend(self._format_module_detailed(pf, summary))
        
        # Footer
        lines.extend([
            "",
            "---",
            "",
            f"_Generated: {datetime.now().isoformat()}_",
            f"_Modules documented: {len(parsed_files)}_",
        ])
        
        # Write file
        tech_path = self.output_dir / "TECHNICAL_DOC.md"
        tech_path.write_text("\n".join(lines), encoding="utf-8")
        
        return tech_path
    
    def _format_module_detailed(
        self,
        parsed_file: ParsedFile,
        summary: Optional[ModuleSummary]
    ) -> List[str]:
        """Format detailed documentation for a single module."""
        
        module_name = Path(parsed_file.file_path).stem
        
        lines = [
            f"### {module_name}",
            "",
            f"📄 `{parsed_file.file_path}`",
            "",
        ]
        
        # Module docstring
        if parsed_file.module_docstring:
            lines.extend([
                "**Description:**",
                "",
                f"> {parsed_file.module_docstring}",
                "",
            ])
        
        # LLM-generated purpose (if available)
        if summary:
            lines.extend([
                "**Purpose:**",
                "",
                summary.purpose,
                "",
            ])
            
            if summary.responsibilities:
                lines.append("**Responsibilities:**")
                lines.append("")
                for resp in summary.responsibilities:
                    lines.append(f"- {resp}")
                lines.append("")
        
        # Classes
        if parsed_file.classes:
            lines.extend([
                "#### Classes",
                "",
            ])
            
            for cls in parsed_file.classes:
                lines.extend(self._format_class(cls))
        
        # Functions
        if parsed_file.functions:
            lines.extend([
                "#### Functions",
                "",
            ])
            
            for func in parsed_file.functions:
                lines.extend(self._format_function(func))
        
        # Dependencies
        if parsed_file.imports:
            lines.extend([
                "#### Dependencies",
                "",
            ])
            
            for imp in parsed_file.imports[:10]:  # Limit to 10
                if hasattr(imp, 'module'):
                    lines.append(f"- `{imp.module}`")
                else:
                    lines.append(f"- `{imp}`")
            
            if len(parsed_file.imports) > 10:
                lines.append(f"- _...and {len(parsed_file.imports) - 10} more_")
            
            lines.append("")
        
        lines.extend(["---", ""])
        
        return lines
    
    def _format_class(self, cls: ClassInfo) -> List[str]:
        """Format a class for documentation."""
        
        lines = [
            f"##### `class {cls.name}`",
            "",
        ]
        
        # Inheritance
        if hasattr(cls, 'base_classes') and cls.base_classes:
            bases = ", ".join(cls.base_classes)
            lines.append(f"_Inherits from: `{bases}`_")
            lines.append("")
        
        # Decorators
        if hasattr(cls, 'decorators') and cls.decorators:
            decorators = ", ".join(f"@{d}" for d in cls.decorators)
            lines.append(f"_Decorators: {decorators}_")
            lines.append("")
        
        # Docstring
        if cls.docstring:
            lines.extend([
                cls.docstring,
                "",
            ])
        
        # Methods
        if cls.methods:
            lines.append("**Methods:**")
            lines.append("")
            lines.append("| Method | Parameters | Returns | Description |")
            lines.append("|--------|------------|---------|-------------|")
            
            for method in cls.methods:
                # Skip private methods in table (can include if needed)
                if hasattr(method, 'is_private') and method.is_private and method.name != '__init__':
                    continue
                
                # Format parameters
                if hasattr(method, 'params') and method.params:
                    if hasattr(method.params[0], 'name'):
                        params = ", ".join(
                            p.name for p in method.params 
                            if p.name not in ('self', 'cls')
                        )
                    else:
                        params = ", ".join(
                            str(p) for p in method.params 
                            if str(p) not in ('self', 'cls')
                        )
                else:
                    params = ""
                
                # Format return type
                returns = method.returns if method.returns else "None"
                
                # Format description (first line of docstring)
                desc = ""
                if method.docstring:
                    desc = method.docstring.split('\n')[0][:50]
                    if len(method.docstring.split('\n')[0]) > 50:
                        desc += "..."
                
                lines.append(f"| `{method.name}` | `{params}` | `{returns}` | {desc} |")
            
            lines.append("")
        
        return lines
    
    def _format_function(self, func: FunctionInfo) -> List[str]:
        """Format a function for documentation."""
        
        # Build signature
        if hasattr(func, 'signature'):
            signature = func.signature
        else:
            # Build manually
            if hasattr(func, 'params') and func.params:
                if hasattr(func.params[0], 'name'):
                    params = ", ".join(str(p) for p in func.params)
                else:
                    params = ", ".join(func.params)
            else:
                params = ""
            
            async_prefix = "async " if hasattr(func, 'is_async') and func.is_async else ""
            returns = f" -> {func.returns}" if func.returns else ""
            signature = f"{async_prefix}def {func.name}({params}){returns}"
        
        lines = [
            f"##### `{func.name}`",
            "",
            "```python",
            signature,
            "```",
            "",
        ]
        
        # Docstring
        if func.docstring:
            lines.extend([
                func.docstring,
                "",
            ])
        
        # Parameters detail (if we have type info)
        if hasattr(func, 'params') and func.params:
            params_with_types = [
                p for p in func.params 
                if hasattr(p, 'type_hint') and p.type_hint
            ]
            
            if params_with_types:
                lines.append("**Parameters:**")
                lines.append("")
                for p in params_with_types:
                    if p.name in ('self', 'cls'):
                        continue
                    default = f" = `{p.default_value}`" if hasattr(p, 'default_value') and p.default_value else ""
                    lines.append(f"- `{p.name}` ({p.type_hint}){default}")
                lines.append("")
        
        # Return type
        if func.returns:
            lines.extend([
                f"**Returns:** `{func.returns}`",
                "",
            ])
        
        return lines
    
    # ================================================================
    # API REFERENCE
    # ================================================================
    
    def _generate_api_reference(
        self,
        parsed_files: List[ParsedFile],
        summary_lookup: Dict[str, ModuleSummary],
        project_name: str
    ) -> Path:
        """Generate API_REFERENCE.md - complete API documentation."""
        
        lines = [
            f"# {project_name} - API Reference",
            "",
            f"> 📖 Complete API Documentation | Generated: {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "## Table of Contents",
            "",
        ]
        
        # Build TOC
        sorted_files = sorted(parsed_files, key=lambda x: x.file_path)
        
        for pf in sorted_files:
            module_name = Path(pf.file_path).stem
            anchor = module_name.lower().replace("_", "-")
            
            lines.append(f"- [{module_name}](#{anchor})")
            
            for cls in pf.classes:
                cls_anchor = cls.name.lower().replace("_", "-")
                lines.append(f"  - [class {cls.name}](#{cls_anchor})")
        
        lines.extend(["", "---", ""])
        
        # Document each module
        for pf in sorted_files:
            lines.extend(self._format_api_module(pf, summary_lookup.get(pf.file_path)))
        
        # Write file
        api_path = self.output_dir / "API_REFERENCE.md"
        api_path.write_text("\n".join(lines), encoding="utf-8")
        
        return api_path
    
    def _format_api_module(
        self,
        parsed_file: ParsedFile,
        summary: Optional[ModuleSummary]
    ) -> List[str]:
        """Format complete API documentation for a module."""
        
        module_name = Path(parsed_file.file_path).stem
        
        lines = [
            f"## {module_name}",
            "",
            f"**File:** `{parsed_file.file_path}`",
            "",
        ]
        
        if parsed_file.module_docstring:
            lines.extend([
                "**Description:**",
                "",
                parsed_file.module_docstring,
                "",
            ])
        
        if summary:
            lines.extend([
                "**Purpose:**",
                "",
                summary.purpose,
                "",
            ])
        
        # Classes with full details
        for cls in parsed_file.classes:
            lines.extend(self._format_api_class(cls))
        
        # Standalone functions
        if parsed_file.functions:
            lines.extend([
                "### Functions",
                "",
            ])
            
            for func in parsed_file.functions:
                lines.extend(self._format_api_function(func))
        
        lines.extend(["---", ""])
        
        return lines
    
    def _format_api_class(self, cls: ClassInfo) -> List[str]:
        """Format complete API documentation for a class."""
        
        lines = [
            f"### class `{cls.name}`",
            "",
        ]
        
        # Full class declaration
        if hasattr(cls, 'base_classes') and cls.base_classes:
            bases = ", ".join(cls.base_classes)
            lines.append(f"```python")
            lines.append(f"class {cls.name}({bases}):")
            lines.append(f"```")
        else:
            lines.append(f"```python")
            lines.append(f"class {cls.name}:")
            lines.append(f"```")
        
        lines.append("")
        
        if cls.docstring:
            lines.extend([cls.docstring, ""])
        
        # All methods
        if cls.methods:
            lines.append("#### Methods")
            lines.append("")
            
            for method in cls.methods:
                lines.extend(self._format_api_function(method, is_method=True))
        
        return lines
    
    def _format_api_function(
        self,
        func: FunctionInfo,
        is_method: bool = False
    ) -> List[str]:
        """Format complete API documentation for a function."""
        
        # Build full signature
        async_prefix = "async " if hasattr(func, 'is_async') and func.is_async else ""
        
        if hasattr(func, 'params') and func.params:
            if hasattr(func.params[0], 'name'):
                param_parts = []
                for p in func.params:
                    if hasattr(p, 'type_hint') and p.type_hint:
                        if hasattr(p, 'default_value') and p.default_value:
                            param_parts.append(f"{p.name}: {p.type_hint} = {p.default_value}")
                        else:
                            param_parts.append(f"{p.name}: {p.type_hint}")
                    else:
                        param_parts.append(p.name)
                params = ", ".join(param_parts)
            else:
                params = ", ".join(str(p) for p in func.params)
        else:
            params = ""
        
        returns = f" -> {func.returns}" if func.returns else ""
        signature = f"{async_prefix}def {func.name}({params}){returns}"
        
        lines = [
            f"##### `{func.name}`",
            "",
            "```python",
            signature,
            "```",
            "",
        ]
        
        if func.docstring:
            lines.extend([func.docstring, ""])
        
        # Detailed parameters
        if hasattr(func, 'params') and func.params:
            real_params = [
                p for p in func.params 
                if (hasattr(p, 'name') and p.name not in ('self', 'cls'))
                or (not hasattr(p, 'name') and str(p) not in ('self', 'cls'))
            ]
            
            if real_params:
                lines.append("**Parameters:**")
                lines.append("")
                
                for p in real_params:
                    if hasattr(p, 'name'):
                        name = p.name
                        type_hint = p.type_hint if hasattr(p, 'type_hint') and p.type_hint else "Any"
                        default = p.default_value if hasattr(p, 'default_value') and p.default_value else None
                    else:
                        name = str(p)
                        type_hint = "Any"
                        default = None
                    
                    if default:
                        lines.append(f"- **{name}** (`{type_hint}`, default=`{default}`)")
                    else:
                        lines.append(f"- **{name}** (`{type_hint}`)")
                
                lines.append("")
        
        if func.returns:
            lines.extend([
                "**Returns:**",
                "",
                f"`{func.returns}`",
                "",
            ])
        
        return lines


# Backward compatible class
class DocumentationGenerator(EnhancedDocumentationGenerator):
    """Alias for backward compatibility."""
    pass


if __name__ == "__main__":
    # Test with sample data
    from models.parsed_file import ProjectAnalysis, ModuleSummary
    
    test_analysis = ProjectAnalysis(
        project_purpose="A test project",
        architecture_overview="Modular design",
        entry_points=["main.py"],
        module_relationships="Pipeline pattern",
        design_patterns=["Factory", "Strategy"]
    )
    
    test_summaries = [
        ModuleSummary(
            file_path="main.py",
            purpose="Entry point",
            responsibilities=["Orchestration"],
            key_components=["main()"],
            dependencies=["sys"]
        )
    ]
    
    # Would need actual ParsedFile for full test
    generator = EnhancedDocumentationGenerator(output_dir="test_docs")
    print("Enhanced generator ready!")