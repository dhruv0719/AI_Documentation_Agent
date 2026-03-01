# test/test_change_detection.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))  # Add project root to path
from core.change_detector import ChangeDetector
from models.parsed_file import ModuleSummary

def test_change_detection():
    """Test change detection on a real project."""
    
    project_root = r"D:\AI_Documentation_Agent"
    
    # Mock file list (from scanner)
    files = ["main.py", "core/scanner.py", "parsers/python_parser.py", "models/parsed_file.py", "analysis/analyzer.py"]
    
    detector = ChangeDetector(project_root)
    
    # First run
    print("="*60)
    print("FIRST RUN (All files are new)")
    print("="*60)
    changes = detector.detect_changes(files)
    print(changes.summary())
    
    # Simulate analysis - create dummy summaries
    summaries = {}
    for file in files:
        summaries[file] = ModuleSummary(
            file_path=file,
            purpose=f"Mock summary for {file}",
            responsibilities=["Task 1", "Task 2"],
            key_components=["Component A", "Component B"],
            dependencies=["os", "sys"]
        )
    
    # Update metadata
    detector.update_metadata(files, summaries, "Test Project")
    print("\n✓ Metadata saved\n")
    
    # Second run (no changes)
    print("="*60)
    print("SECOND RUN (No changes)")
    print("="*60)
    changes = detector.detect_changes(files)
    print(changes.summary())
    
    # Test cached summary retrieval
    cached = detector.get_cached_summary("main.py")
    if cached:
        print(f"\n✓ Retrieved cached summary for main.py:")
        print(f"  Purpose: {cached.purpose}")
    
    # Third run (simulate file modification by manually changing hash)
    print("\n" + "="*60)
    print("THIRD RUN (Simulate main.py modification)")
    print("="*60)
    print("  [In real usage, you'd edit the file]")
    print("  [Here we'll just pretend it changed]\n")
    
    # Actually modify a file to see real change detection
    test_file = Path(project_root) / "test_temp.py"
    test_file.write_text("print('v1')")
    
    files_with_temp = files + ["test_temp.py"]
    changes = detector.detect_changes(files_with_temp)
    print(changes.summary())

    summaries["test_temp.py"] = ModuleSummary(
        file_path="test_temp.py",
        purpose="Temp test file",
        responsibilities=["Testing"],
        key_components=["print"],
        dependencies=[]
    )
    detector.update_metadata(files_with_temp, summaries, "Test Project")
    print("✓ Metadata updated with test_temp.py\n")
    
    # Modify the temp file
    test_file.write_text("print('v2')")
    changes = detector.detect_changes(files_with_temp)
    print("\nAfter modifying test_temp.py:")
    print(changes.summary())
    
    # Cleanup
    test_file.unlink()
    print("\n✓ Test complete!")

if __name__ == "__main__":
    test_change_detection()