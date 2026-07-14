import os
import unittest
from pathlib import Path

from core.config import ConfigManager
from core.errors import ConfigurationError
from test.support import temporary_project

class ConfigManagerTests(unittest.TestCase):
    def test_missing_file_raises(self):
        with temporary_project() as root:
            missing = root / "nonexistent.yaml"
            with self.assertRaises(FileNotFoundError):
                ConfigManager().load_from_file(missing)

    def test_empty_yaml_uses_defaults(self):
        with temporary_project() as root:
            cfg_path = root / ".docagent.yaml"
            cfg_path.write_text("", encoding="utf-8")
            cfg = ConfigManager().load_from_file(cfg_path)
            self.assertEqual(cfg.llm.provider, "groq")
            self.assertTrue(cfg.scanner.include_extensions)

    def test_invalid_temperature_raises(self):
        with temporary_project() as root:
            cfg_path = root / ".docagent.yaml"
            cfg_path.write_text("llm:\n  temperature: 4\n", encoding="utf-8")
            with self.assertRaises(ConfigurationError):
                ConfigManager().load_from_file(cfg_path)

    def test_env_override_applied(self):
        os.environ["OPENAI_API_KEY"] = "dummy-key"
        try:
            with temporary_project() as root:
                cfg_path = root / ".docagent.yaml"
                cfg_path.write_text("", encoding="utf-8")
                cfg = ConfigManager().load_from_file(cfg_path)
                self.assertEqual(cfg.llm.api_key, "dummy-key")
        finally:
            os.environ.pop("OPENAI_API_KEY", None)

    def test_precedence_order(self):
        os.environ["OPENAI_API_KEY"] = "env-key"
        try:
            with temporary_project() as root:
                cfg_path = root / ".docagent.yaml"
                cfg_path.write_text("llm:\n  provider: openai\n", encoding="utf-8")
                cfg = ConfigManager().load_from_file(cfg_path)
                self.assertEqual(cfg.llm.provider, "openai")
                self.assertEqual(cfg.llm.api_key, "env-key")
        finally:
            os.environ.pop("OPENAI_API_KEY", None)
