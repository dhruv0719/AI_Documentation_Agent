# core/frameworks.py
"""
Utility for detecting common frameworks in a project.

Fix applied: _detect_py_from_imports previously read Path(node.path) directly,
which is a project-relative path, not a real filesystem path - this only
happened to work if the process's cwd was the project root. Now resolves
against project_root explicitly, so it works regardless of cwd.
"""

import json
from pathlib import Path
from typing import List

from models.scan_result import FileNode

JS_FRAMEWORKS = {
    "react": "react",
    "next": "next",
    "vue": "vue",
    "angular": "angular",
    "svelte": "svelte",
    "express": "express",
    "nuxt": "nuxt",
    "nestjs": "nestjs",
    "gatsby": "gatsby",
}

PY_FRAMEWORKS = {
    "django": "django",
    "flask": "flask",
    "fastapi": "fastapi",
    "pyramid": "pyramid",
    "bottle": "bottle",
}


def _detect_js_from_package_json(project_root: Path) -> List[str]:
    pkg_path = project_root / "package.json"
    found: List[str] = []
    if not pkg_path.is_file():
        return found
    try:
        data = json.loads(pkg_path.read_text(encoding="utf-8"))
    except Exception:
        return found
    for section in ("dependencies", "devDependencies"):
        deps = data.get(section, {})
        for dep in deps:
            name = dep.lower()
            if name in JS_FRAMEWORKS:
                found.append(JS_FRAMEWORKS[name])
    return list(set(found))


def _detect_py_from_imports(project_root: Path, file_nodes: List[FileNode]) -> List[str]:
    """Inspect Python file contents for framework imports.

    node.path is project-relative (e.g. "app.py" or "subdir/util.py") - it must
    be joined with project_root to get a real filesystem path. Reading it bare
    only worked by accident when cwd == project_root.
    """
    found: List[str] = []
    for node in file_nodes:
        if node.language != "python":
            continue
        full_path = project_root / node.path
        try:
            text = full_path.read_text(encoding="utf-8")
        except Exception:
            continue
        for lib, label in PY_FRAMEWORKS.items():
            if f"import {lib}" in text or f"from {lib}" in text:
                found.append(label)
    return list(set(found))


def detect_frameworks(project_root: Path, file_nodes: List[FileNode]) -> List[str]:
    """Detect frameworks used in the project.

    Returns a list of unique framework identifiers (e.g. "react", "django").
    """
    project_root = Path(project_root)
    frameworks: List[str] = []
    frameworks.extend(_detect_js_from_package_json(project_root))
    frameworks.extend(_detect_py_from_imports(project_root, file_nodes))
    seen = set()
    unique = []
    for f in frameworks:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique