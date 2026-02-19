# scanner.py
from pathlib import Path
from typing import List

class Scanner:
    def scan_project(self, project_path: str, ignore_dirs: List[str] = None) -> List[str]:
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

        try:
            project_path = Path(project_path)

            python_files = []
            for file in project_path.glob('**/*.py'):
                relative_path = str(file.relative_to(project_path))
                if not any(ignore_dir in relative_path for ignore_dir in ignore_dirs):
                    python_files.append(relative_path)
            return python_files
            
        except Exception as e:
            print(f"Error accessing project path: {e}")
            return []
        

if __name__ == "__main__":
    scanner = Scanner()
    project_path = input("Enter the path to the project: ")
    ignore_dirs_input = ["venv", ".git", "node_modules", "__pycache__", ".venv", "dist", "build", ".pytest_cache", ".pyc"]
    python_files = scanner.scan_project(project_path, ignore_dirs_input)
    print("Python files found in the project:")
    for file in python_files:
        print(file)

