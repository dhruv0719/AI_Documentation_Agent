"""Tests for Phase 1 platform contracts and configuration foundations."""

import os
import unittest
from pathlib import Path

from core.config import ConfigManager
from core.environment import load_dotenv
from core.errors import ConfigurationError
from models.language import SourceLanguage
from parsers.base_parser import BaseParser
from parsers.python_parser import PythonParser
from test.support import temporary_project


class FoundationTests(unittest.TestCase):
    def test_python_parser_implements_shared_contract(self) -> None:
        parser = PythonParser()
        self.assertIsInstance(parser, BaseParser)
        self.assertEqual(parser.language, SourceLanguage.PYTHON)
        self.assertEqual(parser.supported_extensions, [".py"])

    def test_python_parser_records_source_language(self) -> None:
        with temporary_project() as project_root:
            source = project_root / "sample.py"
            source.write_text("def documented() -> str:\n    return 'ok'\n", encoding="utf-8")
            parsed = PythonParser(project_root).parse_file("sample.py")
            self.assertIsNotNone(parsed)
            self.assertEqual(parsed.language, SourceLanguage.PYTHON)

    def test_empty_yaml_configuration_uses_defaults(self) -> None:
        with temporary_project() as project_root:
            config_path = project_root / ".docagent.yaml"
            config_path.write_text("", encoding="utf-8")
            config = ConfigManager().load_from_file(config_path)
            self.assertEqual(config.llm.provider, "groq")

    def test_invalid_configuration_is_reported_as_domain_error(self) -> None:
        with temporary_project() as project_root:
            config_path = project_root / ".docagent.yaml"
            config_path.write_text("llm:\n  temperature: 4\n", encoding="utf-8")
            with self.assertRaises(ConfigurationError):
                ConfigManager().load_from_file(config_path)

    def test_dotenv_never_overwrites_process_environment(self) -> None:
        key = "DOCAGENT_FOUNDATION_TEST_KEY"
        original = os.environ.get(key)
        try:
            with temporary_project() as root:
                (root / ".env").write_text(
                    f"{key}=from_file\nSECOND_VALUE='loaded value'\n",
                    encoding="utf-8",
                )
                os.environ[key] = "from_process"
                loaded = load_dotenv(root)
                self.assertNotIn(key, loaded)
                self.assertEqual(os.environ[key], "from_process")
                self.assertEqual(os.environ["SECOND_VALUE"], "loaded value")
        finally:
            if original is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original
            os.environ.pop("SECOND_VALUE", None)
