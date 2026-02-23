# main.py
from typing import List
from models import ParsedFile
from parser import parse_file
from scanner import scan_project

def analyze_project(project_path: str) -> List[ParsedFile]:
    """
    Scan and parse all Python

    Args:
        project_path: Path to the project root
    
    Returns:
        List of successfully parsed files
    """
    print(f"Analyzing project: {project_path}\n")

    # Scan for Python files
    python_file = scan_project(
        project_path, 
        ignore_dirs=["venv", ".git", "node_modules", "__pycache__", ".venv", "dist", "build", ".pytest_cache"]
    )

    print(f"Found {len(python_file)} Python files\n")
    
    # Parse each file
    parsed_files = []
    failed_files = []

    for file in python_file:
        parsed = parse_file(file, project_root=project_path)
        if parsed: # Only append if parsing was successful
            parsed_files.append(parsed)
        else:
            failed_files.append(file)

    # Summary
    print(f"\n{'='*60}")
    print(f"PARSING COMPLETE")
    print(f"\n{'='*60}")
    print(f"Successfully parsed: {len(parsed_files)} files")
    print(f"Failed to parse: {len(failed_files)} files")

    if failed_files:
        print("\nFailed files:")
        for f in failed_files:
            print(f"  - {f}")

    # Calculate statistics
    total_classes = sum(len(pf.classes) for pf in parsed_files)
    total_functions = sum(len(pf.functions) for pf in parsed_files)
    total_imports = sum(len(pf.imports) for pf in parsed_files)

    print(f"\n{'='*60}")
    print(f"PROJECT STATISTICS")
    print(f"{'='*60}")
    print(f"Total classes: {total_classes}")
    print(f"Total functions: {total_functions}")
    print(f"Total imports: {total_imports}")
    
    return parsed_files

def print_parsed_file_details(parsed_file: ParsedFile):
    """Print detailed information about a parsed file."""
    print(f"\n{'='*60}")
    print(f"FILE: {parsed_file.file_path}")
    print(f"{'='*60}")
    
    if parsed_file.module_docstring:
        print(f"\nModule Docstring:\n  {parsed_file.module_docstring}")
    
    if parsed_file.imports:
        print(f"\nImports ({len(parsed_file.imports)}):")
        for imp in parsed_file.imports:
            print(f"  - {imp}")
    
    if parsed_file.classes:
        print(f"\nClasses ({len(parsed_file.classes)}):")
        for cls in parsed_file.classes:
            print(f"\n  Class: {cls.name}")
            if cls.docstring:
                print(f"    Docstring: {cls.docstring}")
            if cls.methods:
                print(f"    Methods ({len(cls.methods)}):")
                for method in cls.methods:
                    params_str = ", ".join(method.params)
                    return_str = f" -> {method.returns}" if method.returns else ""
                    print(f"      - {method.name}({params_str}){return_str}")
                    if method.docstring:
                        print(f"        Doc: {method.docstring}")
    
    if parsed_file.functions:
        print(f"\nFunctions ({len(parsed_file.functions)}):")
        for func in parsed_file.functions:
            params_str = ", ".join(func.params)
            return_str = f" -> {func.returns}" if func.returns else ""
            print(f"  - {func.name}({params_str}){return_str}")
            if func.docstring:
                print(f"    Doc: {func.docstring}")

if __name__ == "__main__":
    project_path = input("Enter project path: ")
    parsed_files = analyze_project(project_path)

    # Ask if user wants to see detailed breakdown
    show_details = input("\nShow detailed file breakdown? (y/n): ").lower()
    if show_details == 'y':
        for parsed in parsed_files:
            print_parsed_file_details(parsed)