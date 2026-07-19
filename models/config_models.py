# models/config_models.py
"""Data models for configuration settings."""

import os
import json
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "groq"  # openai, groq, local
    api_key: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 4096

    # LLM Models
    small_model: str = "openai/gpt-oss-20b"
    medium_model: str = "openai/gpt-oss-120b"
    large_model: str = "llama-3.3-70b-versatile"
    
    # Model for project synthesis (always needs the best)
    synthesis_model: str = "llama-3.3-70b-versatile"

    def __post_init__(self):
        if self.api_key is None:
            env_map = {
                "openai": "OPENAI_API_KEY",
                "groq": "GROQ_API_KEY",
            }
            env_var = env_map.get(self.provider)
            if env_var:
                self.api_key = os.getenv(env_var)

    def get_model(self, size: str = "medium") -> str:
        """
        Get model name by size category.
        
        Args:
            size: "small", "medium", or "large"
            
        Returns:
            Model name string
        """
        return {
            "small": self.small_model,
            "medium": self.medium_model,
            "large": self.large_model,
            "synthesis": self.synthesis_model,
        }.get(size, self.medium_model)

@dataclass
class ScannerConfig:
    """Scanner configuration."""
    ignore_dirs: List[str] = field(default_factory=lambda: [
        # Python
        "__pycache__",
        ".venv",
        "venv",
        "env",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        "htmlcov",
        "site-packages",
        # JavaScript / TypeScript
        "node_modules",
        "dist",
        "build",
        "out",
        "coverage",
        ".next",
        ".nuxt",
        ".turbo",
        ".parcel-cache",
        ".svelte-kit",
        ".expo",
        ".angular",
        ".vercel",
        ".cache",
        ".turbo",
        "tmp",
        # Editor / VCS
        ".git",
        ".idea",
        ".vscode",
    ])
    
    include_extensions: List[str] = field(default_factory=lambda: [
        ".py", ".js", ".jsx", ".ts", ".tsx"
    ])
    max_file_size_bytes: int = 100_000  # Skip files larger than 100KB

@dataclass
class OutputConfig:
    """Output configuration."""
    output_dir: Path = field(default_factory=lambda: Path("./docs_output"))
    readme_filename: str = "README.md"
    technical_filename: str = "TECHNICAL_DOC.md"
    api_reference_filename: str = "API_REFERENCE.md"
    include_timestamp: bool = True

@dataclass
class ChangeDetectionConfig:
    """Change detection configuration."""
    enabled: bool = True
    metadata_dir: Path = field(default_factory=lambda: Path(".docagent"))
    metadata_filename: str = "metadata.json"
    force_reanalysis: bool = False


@dataclass
class Config:
    """Main configuration container."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    scanner: ScannerConfig = field(default_factory=ScannerConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    change_detection: ChangeDetectionConfig = field(default_factory=ChangeDetectionConfig)

    # Project settings
    project_name: Optional[str] = None
    project_root: Optional[Path] = None
    
    # Logging
    log_level: str = "INFO"
    verbose: bool = False

    # Feature flags
    enable_dependency_graph: bool = False
    enable_quality_metrics: bool = False

    def validate(self) -> None:
        """Validate values that can be checked without external services."""
        if not self.llm.provider or not isinstance(self.llm.provider, str):
            raise ValueError("llm.provider must be a non-empty string")
        if not 0 <= self.llm.temperature <= 2:
            raise ValueError("llm.temperature must be between 0 and 2")
        if self.llm.max_tokens <= 0:
            raise ValueError("llm.max_tokens must be greater than zero")
        if not self.scanner.include_extensions:
            raise ValueError("scanner.include_extensions must not be empty")
        if any(not extension.startswith(".") for extension in self.scanner.include_extensions):
            raise ValueError("scanner.include_extensions entries must begin with '.'")
        if self.scanner.max_file_size_bytes <= 0:
            raise ValueError("scanner.max_file_size_bytes must be greater than zero")
        if not self.output.readme_filename.endswith(".md"):
            raise ValueError("output.readme_filename must be a Markdown filename")
