"""Deterministic change-detection tests."""

import unittest
from pathlib import Path

from core.change_detector import ChangeDetector
from models.parsed_file import ModuleSummary
from test.support import temporary_project


def make_summary(file_path: str) -> ModuleSummary:
    return ModuleSummary(
        file_path=file_path,
        purpose="Test module",
        responsibilities=["Test"],
        key_components=["test"],
        dependencies=[],
    )


class ChangeDetectorTests(unittest.TestCase):
    def test_detects_changes_for_an_external_project_root(self) -> None:
        """Relative scanner paths must be resolved against the supplied project."""
        with temporary_project() as project_root:
            source = project_root / "package" / "module.py"
            source.parent.mkdir()
            source.write_text("def first():\n    return 1\n", encoding="utf-8")
            files = ["package/module.py"]

            detector = ChangeDetector(project_root)
            first = detector.detect_changes(files)
            self.assertEqual(first.added_files, files)

            detector.update_metadata(files, {files[0]: make_summary(files[0])}, "External Project")
            second = ChangeDetector(project_root).detect_changes(files)
            self.assertFalse(second.has_changes)

            source.write_text("def first():\n    return 2\n", encoding="utf-8")
            third = ChangeDetector(project_root).detect_changes(files)
            self.assertEqual(third.modified_files, files)
