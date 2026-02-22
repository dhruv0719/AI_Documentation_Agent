# scanner.py
from pathlib import Path
from typing import List


def scan_project(project_path: str, ignore_dirs: List[str] = None) -> List[str]:
    """
    Scan a project directory and return all Python files.
    
    Args:
        project_path: Path to the project root.
        ignore_dirs: Directories to ignore during scanning.

    Returns:
        List of relative path to .py files in the project.
    """    
    if ignore_dirs is None:
        ignore_dirs = []

    project_path = Path(project_path)
    if not project_path.exists():
        raise FileNotFoundError(f"Path does not exist: {project_path}")
    if not project_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {project_path}")
    
    python_files = []
    for file in project_path.glob('**/*.py'):
        relative_path = str(file.relative_to(project_path))

        # if not any(ignore_dir in relative_path for ignore_dir in ignore_dirs):
        #     python_files.append(relative_path)
        """The Problem with the above code is that it will ignore any file that has the ignore_dir in its path, even if it's not in the ignore_dir. For example, if you have a file called "venv.py" it will be ignored because it contains "venv" in its name. To fix this, we can check if the file is actually in one of the ignore_dirs."""
        if not any(part in ignore_dirs for part in file.relative_to(project_path).parts):
            python_files.append(relative_path)
        
    return python_files
            

if __name__ == "__main__":
    project_path = input("Enter the path to the project: ")
    ignore_dirs_input = ["venv", ".git", "node_modules", "__pycache__", ".venv", "dist", "build", ".pytest_cache"]

    try:
        python_files = scan_project(project_path, ignore_dirs_input)
        print(f"Found {len(python_files)} Python files:")
        for file in python_files:
            print(f"{file}")
    
    except Exception as e:
        print(f"Error scanning project: {e}")