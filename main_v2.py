# main_v2.py
"""Main orchestrator with change detection (V2)."""
from typing import List
from pathlib import Path
from models.parsed_file import ParsedFile
from parsers.python_parser import parse_file  # Your existing parser
from core.scanner import scan_project         # Your existing scanner
from analysis.analyzer import CodeAnalyzer    # Your existing analyzer
from generation.generator import DocumentationGenerator  # Your existing generator
from core.change_detector import ChangeDetector  # NEW!

def generate_documentation(
    project_path: str, 
    project_name: str = None, 
    force: bool = False
):
    """
    Complete pipeline with change detection.
    
    Args:
        project_path: Path to project root
        project_name: Name of project
        force: If True, ignore cache and reanalyze everything
    """
    if project_name is None:
        project_name = Path(project_path).name
    
    print(f"\n{'='*60}")
    print(f"CODE DOCUMENTATION AGENT V2")
    print(f"{'='*60}")
    print(f"Project: {project_name}")
    print(f"Path: {project_path}")
    print(f"Mode: {'FORCE (full analysis)' if force else 'INCREMENTAL'}\n")
    
    # ===== PHASE 1: SCANNING =====
    print(f"{'='*60}")
    print("PHASE 1: SCANNING PROJECT")
    print(f"{'='*60}\n")
    
    python_files = scan_project(
        project_path, 
        ignore_dirs=["venv", ".git", "node_modules", "__pycache__", ".venv", "dist", "build", ".pytest_cache", ".docagent"]
    )
    print(f"✓ Found {len(python_files)} Python files\n")
    
    # ===== PHASE 2: CHANGE DETECTION =====
    print(f"{'='*60}")
    print("PHASE 2: DETECTING CHANGES")
    print(f"{'='*60}\n")
    
    detector = ChangeDetector(project_path)
    
    if force:
        # Force full analysis
        from models.change_report import ChangeReport
        changes = ChangeReport(
            added_files=python_files,
            modified_files=[],
            deleted_files=[],
            unchanged_files=[]
        )
        print("⚠️  Force mode: Analyzing all files\n")
    else:
        # Incremental analysis
        changes = detector.detect_changes(python_files)
        print(changes.summary())
    
    if not changes.has_changes and not force:
        print("✓ No changes detected. Documentation is up to date!\n")
        return
    
    # ===== PHASE 3: PARSING (only changed files) =====
    print(f"{'='*60}")
    print("PHASE 3: PARSING CHANGED FILES")
    print(f"{'='*60}\n")
    
    parsed_files = []
    for file_path in changes.files_to_analyze:
        parsed = parse_file(file_path, project_root=project_path)
        if parsed:
            parsed_files.append(parsed)
            print(f"  ✓ Parsed: {file_path}")
    
    print(f"\n✓ Parsed {len(parsed_files)} changed files\n")
    
    # ===== PHASE 4: MODULE ANALYSIS (only changed files) =====
    print(f"{'='*60}")
    print("PHASE 4: ANALYZING MODULES (LLM)")
    print(f"{'='*60}\n")
    
    analyzer = CodeAnalyzer()
    new_summaries = {}
    
    for parsed_file in parsed_files:
        summary = analyzer.analyze_module(parsed_file)
        new_summaries[parsed_file.file_path] = summary
    
    print(f"\n✓ Analyzed {len(new_summaries)} modules\n")
    
    # ===== MERGE WITH CACHED SUMMARIES =====
    print(f"{'='*60}")
    print("MERGING RESULTS")
    print(f"{'='*60}\n")
    
    all_summaries = []
    
    # Add new/modified summaries
    all_summaries.extend(new_summaries.values())
    print(f"  ✓ New/Modified: {len(new_summaries)} files")
    
    # Add cached summaries for unchanged files
    cached_count = 0
    for file_path in changes.unchanged_files:
        cached = detector.get_cached_summary(file_path)
        if cached:
            all_summaries.append(cached)
            cached_count += 1
    
    print(f"  ✓ Cached: {cached_count} files")
    print(f"\nTotal summaries: {len(all_summaries)}\n")
    
    # Calculate savings
    if cached_count > 0:
        savings_pct = (cached_count / len(python_files)) * 100
        print(f"💰 API Cost Savings: ~{savings_pct:.0f}% ({cached_count}/{len(python_files)} files reused)\n")
    
    # ===== PHASE 5: PROJECT SYNTHESIS =====
    print(f"{'='*60}")
    print("PHASE 5: SYNTHESIZING PROJECT OVERVIEW (LLM)")
    print(f"{'='*60}\n")
    
    project_analysis = analyzer.synthesize_project(all_summaries, project_path)
    print(f"✓ Project synthesis complete\n")
    
    # ===== PHASE 6: SAVE METADATA =====
    print(f"{'='*60}")
    print("PHASE 6: UPDATING METADATA")
    print(f"{'='*60}\n")
    
    all_files = python_files  # All files in project
    all_summaries_dict = {s.file_path: s for s in all_summaries}
    detector.update_metadata(all_files, all_summaries_dict, project_name)
    
    print(f"✓ Metadata saved to .docagent/metadata.json\n")
    
    # ===== PHASE 7: DOCUMENTATION GENERATION =====
    print(f"{'='*60}")
    print("PHASE 7: GENERATING DOCUMENTATION")
    print(f"{'='*60}\n")
    
    doc_generator = DocumentationGenerator(output_dir=f"output/{project_name}")
    generated_files = doc_generator.generate_all(project_analysis, all_summaries, project_name)
    
    print(f"✓ Generated README: {generated_files['readme']}")
    print(f"✓ Generated Technical Doc: {generated_files['technical_doc']}")
    
    # ===== SUMMARY =====
    print(f"\n{'='*60}")
    print("DOCUMENTATION GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"\nProject: {project_name}")
    print(f"Files Analyzed: {len(new_summaries)}")
    print(f"Files Cached: {cached_count}")
    print(f"Output Directory: output/")
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate project documentation (V2)")
    parser.add_argument("path", help="Project path")
    parser.add_argument("--name", help="Project name")
    parser.add_argument("--force", action="store_true", help="Force full reanalysis")
    
    args = parser.parse_args()
    
    try:
        generate_documentation(args.path, args.name, args.force)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()