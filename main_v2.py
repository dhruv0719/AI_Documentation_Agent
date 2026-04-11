# main_v2.py - ENHANCED VERSION
# Shows what to CHANGE, not complete rewrite

"""Main orchestrator with change detection and enhanced docs (V2)."""
from typing import List, Dict
from pathlib import Path
from models.parsed_file import ParsedFile, ModuleSummary
from parsers.python_parser import parse_file
from core.scanner import scan_project
from analysis.analyzer import CodeAnalyzer
from core.change_detector import ChangeDetector


def generate_documentation(
    project_path: str, 
    project_name: str = None, 
    force: bool = False
):
    if project_name is None:
        project_name = Path(project_path).name
    
    print(f"\n{'='*60}")
    print(f"CODE DOCUMENTATION AGENT V2")
    print(f"{'='*60}")
    print(f"Project: {project_name}")
    print(f"Path: {project_path}")
    print(f"Mode: {'FORCE' if force else 'INCREMENTAL'}\n")
    
    # ===== PHASE 1: SCANNING =====
    print(f"\n📁 PHASE 1: SCANNING PROJECT\n")
    
    python_files = scan_project(
        project_path, 
        ignore_dirs=[
            "venv", ".git", "node_modules", "__pycache__", 
            ".venv", "dist", "build", ".pytest_cache", ".docagent"
        ]
    )
    print(f"  ✓ Found {len(python_files)} Python files")
    
    # ===== PHASE 2: CHANGE DETECTION =====
    print(f"\n🔍 PHASE 2: DETECTING CHANGES\n")
    
    detector = ChangeDetector(project_path)
    
    if force:
        from models.change_report import ChangeReport
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
    # KEY CHANGE: Parse ALL files, not just changed ones
    # Why? Generator needs complete picture for docs
    print(f"\n📝 PHASE 3: PARSING FILES\n")
    
    all_parsed_files: Dict[str, ParsedFile] = {}
    
    for file_path in python_files:
        try:
            parsed = parse_file(file_path, project_root=project_path)
            if parsed:
                all_parsed_files[file_path] = parsed
        except Exception as e:
            print(f"  ⚠ Skipping {file_path}: {e}")
    
    print(f"  ✓ Parsed {len(all_parsed_files)} files")
    
    # ===== PHASE 3.5: DEPENDENCY ANALYSIS ===== (NEW!)
    print(f"\n🔗 PHASE 3.5: ANALYZING DEPENDENCIES\n")
    
    dependency_diagram = None
    try:
        from analysis.dependency_analyzer import DependencyAnalyzer
        
        dep_analyzer = DependencyAnalyzer(
            project_path, 
            list(all_parsed_files.values())
        )
        dep_graph = dep_analyzer.build_graph()
        
        print(f"  ✓ Entry points: {dep_graph.entry_points}")
        print(f"  ✓ Circular deps: {len(dep_graph.circular_dependencies)}")
        
        # Generate Mermaid diagram
        dependency_diagram = dep_analyzer.to_mermaid(dep_graph)
        
        # Get optimal analysis order
        analysis_order = dep_graph.get_analysis_order()
        print(f"  ✓ Analysis order computed")
        
    except ImportError:
        print("  ⚠ Dependency analyzer not available, skipping")
    except Exception as e:
        print(f"  ⚠ Dependency analysis failed: {e}")
    
    # ===== PHASE 4: LLM ANALYSIS (only changed files) =====
    print(f"\n🤖 PHASE 4: LLM ANALYSIS\n")
    
    analyzer = CodeAnalyzer()
    new_summaries = {}
    
    files_to_analyze = changes.files_to_analyze
    print(f"  Analyzing {len(files_to_analyze)} files...")
    
    for file_path in files_to_analyze:
        parsed = all_parsed_files.get(file_path)
        if parsed:
            try:
                summary = analyzer.analyze_module(parsed)
                new_summaries[file_path] = summary
                print(f"  ✓ {file_path}")
            except Exception as e:
                print(f"  ✗ {file_path}: {e}")
    
    print(f"\n  ✓ Analyzed {len(new_summaries)} modules")
    
    # ===== MERGE WITH CACHED SUMMARIES =====
    print(f"\n🔄 MERGING RESULTS\n")
    
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
    print(f"  Total: {len(all_summaries)} summaries")
    
    if cached_count > 0:
        savings = (cached_count / len(python_files)) * 100
        print(f"\n  💰 API Savings: ~{savings:.0f}%")
    
    # ===== PHASE 5: PROJECT SYNTHESIS =====
    print(f"\n🏗️ PHASE 5: PROJECT SYNTHESIS\n")
    
    project_analysis = analyzer.synthesize_project(
        list(all_summaries.values()), 
        project_path
    )
    print(f"  ✓ Project synthesis complete")
    
    # ===== PHASE 6: SAVE METADATA =====
    print(f"\n💾 PHASE 6: SAVING METADATA\n")
    
    detector.update_metadata(
        python_files, 
        all_summaries, 
        project_name
    )
    print(f"  ✓ Metadata saved")
    
    # ===== PHASE 7: GENERATE DOCUMENTATION =====
    print(f"\n📄 PHASE 7: GENERATING DOCUMENTATION\n")
    
    # KEY CHANGE: Use enhanced generator with ParsedFile data
    try:
        from generation.enhanced_generator import EnhancedDocumentationGenerator
        
        doc_generator = EnhancedDocumentationGenerator(
            output_dir=f"output/{project_name}"
        )
        
        result = doc_generator.generate_all(
            project_analysis=project_analysis,
            module_summaries=list(all_summaries.values()),
            parsed_files=list(all_parsed_files.values()),  # NEW!
            project_name=project_name,
            dependency_diagram=dependency_diagram  # NEW!
        )
        
        print(f"  ✓ README: {result.readme_path}")
        print(f"  ✓ Technical Doc: {result.technical_doc_path}")
        if result.api_reference_path:
            print(f"  ✓ API Reference: {result.api_reference_path}")
    
    except ImportError:
        # Fallback to basic generator
        from generation.generator import DocumentationGenerator
        
        doc_generator = DocumentationGenerator(
            output_dir=f"output/{project_name}"
        )
        generated = doc_generator.generate_all(
            project_analysis, 
            list(all_summaries.values()), 
            project_name
        )
        
        print(f"  ✓ README: {generated['readme']}")
        print(f"  ✓ Technical Doc: {generated['technical_doc']}")
    
    # ===== SUMMARY =====
    print(f"\n{'='*60}")
    print("✅ DOCUMENTATION GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"  Project: {project_name}")
    print(f"  Files Analyzed: {len(new_summaries)}")
    print(f"  Files Cached: {cached_count}")
    print(f"  Total Documented: {len(all_summaries)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Code Documentation Agent V2"
    )
    parser.add_argument("path", help="Project path")
    parser.add_argument("--name", help="Project name")
    parser.add_argument("--force", action="store_true", help="Force full reanalysis")
    parser.add_argument(
        "--provider", 
        choices=["groq", "openai"], 
        default="groq",
        help="LLM provider"
    )
    
    args = parser.parse_args()
    
    try:
        generate_documentation(args.path, args.name, args.force)
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()