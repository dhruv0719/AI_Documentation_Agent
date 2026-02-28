# main.py
"""Main orchestrator for the Code Documentation Agent."""
from typing import List
from pathlib import Path
from models.parsed_file import ParsedFile
from parsers.python_parser import parse_file
from core.scanner import scan_project
from analysis.analyzer import CodeAnalyzer
from generator import DocumentationGenerator

def generate_documentation(project_path: str, project_name: str = None):
    """
    Complete pipeline: Scan → Parse → Analyze → Generate Docs
    
    Args:
        project_path: Path to the project root
        project_name: Name of the project (uses folder name if not provided)
    """
    # Determine project name
    if project_name is None:
        project_name = Path(project_path).name
    
    print(f"\n{'='*60}")
    print(f"CODE DOCUMENTATION AGENT")
    print(f"{'='*60}")
    print(f"Project: {project_name}")
    print(f"Path: {project_path}\n")
    
    # ===== PHASE 1: SCANNING =====
    print(f"{'='*60}")
    print("PHASE 1: SCANNING PROJECT")
    print(f"{'='*60}\n")
    
    python_files = scan_project(
        project_path, 
        ignore_dirs=["venv", ".git", "node_modules", "__pycache__", ".venv", "dist", "build", ".pytest_cache", ".github"]
    )
    print(f"✓ Found {len(python_files)} Python files\n")
    
    # ===== PHASE 2: PARSING =====
    print(f"{'='*60}")
    print("PHASE 2: PARSING FILES")
    print(f"{'='*60}\n")
    
    parsed_files = []
    failed_files = []
    
    for file_path in python_files:
        parsed = parse_file(file_path, project_root=project_path)
        if parsed:
            parsed_files.append(parsed)
        else:
            failed_files.append(file_path)
    
    print(f"✓ Successfully parsed: {len(parsed_files)} files")
    if failed_files:
        print(f"✗ Failed to parse: {len(failed_files)} files")
        for f in failed_files:
            print(f"  - {f}")
    print()
    
    # ===== PHASE 3: MODULE ANALYSIS =====
    print(f"{'='*60}")
    print("PHASE 3: ANALYZING MODULES (LLM)")
    print(f"{'='*60}\n")
    
    analyzer = CodeAnalyzer()
    module_summaries = []
    
    for parsed_file in parsed_files:
        summary = analyzer.analyze_module(parsed_file)
        module_summaries.append(summary)
    
    print(f"\n✓ Analyzed {len(module_summaries)} modules\n")
    
    # ===== PHASE 4: PROJECT SYNTHESIS =====
    print(f"{'='*60}")
    print("PHASE 4: SYNTHESIZING PROJECT OVERVIEW (LLM)")
    print(f"{'='*60}\n")
    
    project_analysis = analyzer.synthesize_project(module_summaries, project_path)
    
    print(f"✓ Project synthesis complete\n")
    
    # ===== PHASE 5: DOCUMENTATION GENERATION =====
    print(f"{'='*60}")
    print("PHASE 5: GENERATING DOCUMENTATION")
    print(f"{'='*60}\n")
    
    doc_generator = DocumentationGenerator(output_dir=f"output/{project_name}")
    generated_files = doc_generator.generate_all(project_analysis, module_summaries, project_name)
    
    print(f"✓ Generated README: {generated_files['readme']}")
    print(f"✓ Generated Technical Doc: {generated_files['technical_doc']}")
    
    # ===== SUMMARY =====
    print(f"\n{'='*60}")
    print("DOCUMENTATION GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"\nProject: {project_name}")
    print(f"Files Analyzed: {len(module_summaries)}")
    print(f"Output Directory: output/")
    print(f"\nGenerated Files:")
    print(f"  - README.md")
    print(f"  - TECHNICAL_DOC.md")
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    # Get project path from user
    project_path = input("Enter project path: ").strip()
    project_name = input("Enter project name (or press Enter to use folder name): ").strip()
    
    if not project_name:
        project_name = None
    
    try:
        generate_documentation(project_path, project_name)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()