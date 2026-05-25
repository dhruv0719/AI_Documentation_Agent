# main_v2.py - FINAL VERSION (Everything Connected)

"""
Code Documentation Agent V2 - Main Orchestrator

Pipeline:
  SCAN → CHANGE DETECT → PARSE → DEPENDENCY → LLM ANALYZE → GENERATE

Features:
  - Change detection (only re-analyze modified files)
  - Dependency graph analysis
  - Enhanced documentation with code details
  - Multiple LLM provider support
  - Configuration file support
"""

import time
import argparse
from typing import Dict, Optional
from pathlib import Path

from models.parsed_file import ParsedFile, ModuleSummary
from models.change_report import ChangeReport
from parsers.python_parser import PythonParser, parse_file
from core.scanner import scan_project, scan_project_with_tree
from core.change_detector import ChangeDetector
from analysis.analyzer import CodeAnalyzer


def generate_documentation(
    project_path: str,
    project_name: Optional[str] = None,
    force: bool = False,
    provider: str = "groq",
    output_dir: Optional[str] = None
):
    """
    Complete documentation generation pipeline.
    
    Args:
        project_path: Path to project root
        project_name: Name of project (defaults to folder name)
        force: If True, ignore cache and reanalyze everything
        provider: LLM provider ("groq" or "openai")
        output_dir: Output directory (defaults to output/{project_name})
    """
    start_time = time.time()
    
    if project_name is None:
        project_name = Path(project_path).name
    
    if output_dir is None:
        output_dir = f"output/{project_name}"
    
    # Load config if available
    try:
        from core.config import load_config
        config = load_config(project_root=Path(project_path))
        ignore_dirs = config.scanner.ignore_dirs
    except Exception:
        ignore_dirs = [
            "venv", ".git", "node_modules", "__pycache__",
            ".venv", "dist", "build", ".pytest_cache", ".docagent"
        ]
    
    print(f"\n{'='*60}")
    print(f"📚 CODE DOCUMENTATION AGENT V2")
    print(f"{'='*60}")
    print(f"  Project:  {project_name}")
    print(f"  Path:     {project_path}")
    print(f"  Provider: {provider}")
    print(f"  Mode:     {'FORCE' if force else 'INCREMENTAL'}")
    print(f"{'='*60}")
    
    # ===== PHASE 1: SCANNING =====
    print(f"\n📁 PHASE 1: SCANNING PROJECT\n")
    
    scan_result = scan_project_with_tree(project_path, ignore_dirs)
    python_files = scan_result.all_files
    project_tree = scan_result.get_tree_string()
    
    print(f"  ✓ Found {scan_result.total_files} Python files")
    print(f"  ✓ Total size: {scan_result.total_size_mb:.2f} MB")
    print(f"  ✓ Entry points: {scan_result.entry_points}")
    
    if scan_result.total_files == 0:
        print("\n  ⚠️ No Python files found. Nothing to document.")
        return
    
    # ===== PHASE 2: CHANGE DETECTION =====
    print(f"\n🔍 PHASE 2: DETECTING CHANGES\n")
    
    detector = ChangeDetector(project_path)
    
    if force:
        changes = ChangeReport(
            added_files=python_files,
            modified_files=[],
            deleted_files=[],
            unchanged_files=[]
        )
        print("  ⚠️  Force mode: Analyzing all files")
    else:
        changes = detector.detect_changes(python_files)
        print(changes.summary())
    
    if not changes.has_changes and not force:
        print("  ✓ No changes detected. Documentation is up to date!")
        return
    
    # ===== PHASE 3: PARSING ALL FILES =====
    print(f"\n📝 PHASE 3: PARSING FILES\n")
    
    parser = PythonParser(project_root=project_path)
    all_parsed_files: Dict[str, ParsedFile] = {}
    parse_errors = 0
    
    for file_path in python_files:
        try:
            parsed = parser.parse_file(file_path)
            if parsed:
                all_parsed_files[file_path] = parsed
        except Exception as e:
            parse_errors += 1
            print(f"  ⚠ Skipping {file_path}: {e}")
    
    print(f"  ✓ Parsed {len(all_parsed_files)} files")
    if parse_errors > 0:
        print(f"  ⚠ Skipped {parse_errors} files with errors")
    
    # ===== PHASE 3.5: DEPENDENCY ANALYSIS =====
    print(f"\n🔗 PHASE 3.5: ANALYZING DEPENDENCIES\n")
    
    dependency_diagram = None
    dep_summary = None
    
    try:
        from analysis.dependency_analyzer import DependencyAnalyzer
        
        dep_analyzer = DependencyAnalyzer(
            project_path,
            list(all_parsed_files.values())
        )
        dep_graph = dep_analyzer.build_graph()
        
        print(f"  ✓ Modules: {dep_graph.total_modules}")
        print(f"  ✓ Entry points: {dep_graph.entry_points}")
        print(f"  ✓ Circular deps: {len(dep_graph.circular_dependencies)}")
        
        if dep_graph.most_imported:
            top_module, top_count = dep_graph.most_imported[0]
            if top_count > 0:
                print(f"  ✓ Most imported: {Path(top_module).stem} ({top_count} imports)")
        
        # Generate Mermaid diagram
        dependency_diagram = dep_analyzer.generate_mermaid(dep_graph)
        
        # Get analysis order (analyze deps first for better context)
        analysis_order = dep_graph.get_analysis_order()
        
        # Generate dependency summary for docs
        dep_summary = dep_analyzer.generate_summary(dep_graph)
        
    except ImportError:
        print("  ⚠ Dependency analyzer not available, skipping")
    except Exception as e:
        print(f"  ⚠ Dependency analysis failed: {e}")
    
    # ===== PHASE 4: LLM ANALYSIS (only changed files) =====
    print(f"\n🤖 PHASE 4: LLM ANALYSIS\n")
    
    analyzer = CodeAnalyzer(provider=provider)
    new_summaries: Dict[str, ModuleSummary] = {}
    
    files_to_analyze = changes.files_to_analyze
    print(f"  Analyzing {len(files_to_analyze)} files with {provider}...\n")
    
    for i, file_path in enumerate(files_to_analyze, 1):
        parsed = all_parsed_files.get(file_path)
        if parsed:
            try:
                summary = analyzer.analyze_module(parsed)
                new_summaries[file_path] = summary
                print(f"  [{i}/{len(files_to_analyze)}] ✓ {file_path}")
            except Exception as e:
                print(f"  [{i}/{len(files_to_analyze)}] ✗ {file_path}: {e}")
    
    print(f"\n  ✓ Analyzed {len(new_summaries)} modules")
    print(f"  ✓ Tokens used: {analyzer.total_tokens_used}")
    
    # ===== MERGE WITH CACHED SUMMARIES =====
    print(f"\n🔄 PHASE 4.5: MERGING RESULTS\n")
    
    all_summaries: Dict[str, ModuleSummary] = {}
    
    # Add new/modified summaries
    all_summaries.update(new_summaries)
    print(f"  ✓ New/Modified: {len(new_summaries)} files")
    
    # Add cached summaries for unchanged files
    cached_count = 0
    for file_path in changes.unchanged_files:
        cached = detector.get_cached_summary(file_path)
        if cached:
            all_summaries[file_path] = cached
            cached_count += 1
    
    print(f"  ✓ Cached: {cached_count} files")
    print(f"  ✓ Total: {len(all_summaries)} summaries")
    
    if cached_count > 0:
        savings = (cached_count / len(python_files)) * 100
        print(f"  💰 API Savings: ~{savings:.0f}% ({cached_count} files reused)")
    
    # ===== PHASE 5: PROJECT SYNTHESIS =====
    print(f"\n🏗️ PHASE 5: PROJECT SYNTHESIS\n")
    
    project_analysis = analyzer.synthesize_project(
        list(all_summaries.values()),
        project_path
    )
    print(f"  ✓ Project synthesis complete")
    print(f"  ✓ Total tokens used: {analyzer.total_tokens_used}")
    
    # ===== PHASE 6: SAVE METADATA =====
    print(f"\n💾 PHASE 6: SAVING METADATA\n")
    
    detector.update_metadata(
        python_files,
        all_summaries,
        project_name
    )
    print(f"  ✓ Metadata saved to .docagent/metadata.json")
    
    # ===== PHASE 7: GENERATE DOCUMENTATION =====
    print(f"\n📄 PHASE 7: GENERATING DOCUMENTATION\n")
    
    try:
        from generation.enhanced_generator import EnhancedDocumentationGenerator
        
        doc_generator = EnhancedDocumentationGenerator(output_dir=output_dir)
        
        result = doc_generator.generate_all(
            project_analysis=project_analysis,
            module_summaries=list(all_summaries.values()),
            parsed_files=list(all_parsed_files.values()),
            project_name=project_name,
            dependency_diagram=dependency_diagram,
        )
        
        print(f"  ✓ README:        {result.readme_path}")
        print(f"  ✓ Technical Doc: {result.technical_doc_path}")
        if result.api_reference_path:
            print(f"  ✓ API Reference: {result.api_reference_path}")
    
    except ImportError as e:
        print(f"  ⚠ Enhanced generator not available: {e}")
        print(f"  ⚠ Falling back to basic generator...")
        
        from generation.generator import DocumentationGenerator
        
        doc_generator = DocumentationGenerator(output_dir=output_dir)
        generated = doc_generator.generate_all(
            project_analysis,
            list(all_summaries.values()),
            project_name
        )
        
        print(f"  ✓ README:        {generated['readme']}")
        print(f"  ✓ Technical Doc: {generated['technical_doc']}")
    
    # ===== FINAL SUMMARY =====
    elapsed_time = time.time() - start_time
    
    # Calculate stats
    total_classes = sum(len(pf.classes) for pf in all_parsed_files.values())
    total_functions = sum(len(pf.functions) for pf in all_parsed_files.values())
    total_lines = sum(pf.line_count for pf in all_parsed_files.values())
    
    print(f"\n{'='*60}")
    print(f"✅ DOCUMENTATION GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"  Project:            {project_name}")
    print(f"  Files Documented:   {len(all_parsed_files)}")
    print(f"  Files Analyzed:     {len(new_summaries)} (LLM)")
    print(f"  Files Cached:       {cached_count}")
    print(f"  Total Classes:      {total_classes}")
    print(f"  Total Functions:    {total_functions}")
    print(f"  Total Lines:        {total_lines}")
    print(f"  Tokens Used:        {analyzer.total_tokens_used}")
    print(f"  Time:               {elapsed_time:.1f}s")
    print(f"  Output:             {output_dir}/")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Code Documentation Agent V2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_v2.py /path/to/project
  python main_v2.py /path/to/project --name "My Project"
  python main_v2.py /path/to/project --force
  python main_v2.py /path/to/project --provider openai
  python main_v2.py /path/to/project --output ./docs
        """
    )
    
    parser.add_argument("path", help="Path to the project directory")
    parser.add_argument("--name", help="Project name (default: folder name)")
    parser.add_argument("--force", action="store_true", help="Force full reanalysis (ignore cache)")
    parser.add_argument(
        "--provider",
        choices=["groq", "openai"],
        default="groq",
        help="LLM provider to use (default: groq)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output directory (default: output/{project_name})"
    )
    
    args = parser.parse_args()
    
    # Validate path
    if not Path(args.path).exists():
        print(f"\n❌ Error: Path does not exist: {args.path}")
        exit(1)
    
    if not Path(args.path).is_dir():
        print(f"\n❌ Error: Path is not a directory: {args.path}")
        exit(1)
    
    try:
        generate_documentation(
            project_path=args.path,
            project_name=args.name,
            force=args.force,
            provider=args.provider,
            output_dir=args.output
        )
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)