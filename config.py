# config.py
"""
Configuration Management for Code Documentation Agent

Handles all configuration settings including:
- LLM provider settings
- File scanning rules
- Output preferences
"""

import os
from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class LLMConfig(BaseModel):
    """LLM Provider Configuration"""
    
    provider: Literal["openai", "groq", "local"] = Field(
        default="groq",
        description="LLM provider to use"
    )
    model: str = Field(
        default="llama-3.1-8b-instant",
        description="Model name to use"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for the provider"
    )
    temperature: float = Field(
        default=0.3,
        description="Temperature for generation"
    )
    max_tokens: int = Field(
        default=4096,
        description="Maximum tokens in response"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.api_key is None:
            if self.provider == "openai":
                self.api_key = os.getenv("OPENAI_API_KEY")
            elif self.provider == "groq":
                self.api_key = os.getenv("GROQ_API_KEY")


class ScannerConfig(BaseModel):
    """Repository Scanner Configuration"""
    
    # Directories to ignore during scanning
    ignore_dirs: list[str] = Field(
        default=[
            "__pycache__",
            ".git",
            ".github",
            ".venv",
            "venv",
            "env",
            "node_modules",
            ".idea",
            ".vscode",
            "dist",
            "build",
            "egg-info",
            ".tox",
            ".pytest_cache",
            ".mypy_cache",
            ".coverage",
            "htmlcov",
        ]
    )
    
    # File extensions to include
    include_extensions: list[str] = Field(
        default=[".py"]
    )
    
    # Files to ignore
    ignore_files: list[str] = Field(
        default=[
            "__init__.py",
            "setup.py",
            "conftest.py",
        ]
    )
    
    # Maximum file size in bytes (skip large files)
    max_file_size: int = Field(
        default=100_000,  # 100KB
        description="Maximum file size to process"
    )


class OutputConfig(BaseModel):
    """Output Configuration"""
    
    output_dir: Path = Field(
        default=Path("./output"),
        description="Directory for generated documentation"
    )
    overview_filename: str = Field(
        default="README_GENERATED.md"
    )
    technical_filename: str = Field(
        default="TECHNICAL_DOC.md"
    )
    include_timestamp: bool = Field(
        default=True
    )


class AppConfig(BaseModel):
    """Main Application Configuration"""
    
    llm: LLMConfig = Field(default_factory=LLMConfig)
    scanner: ScannerConfig = Field(default_factory=ScannerConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    
    # Logging level
    log_level: str = Field(default="INFO")
    
    # Enable verbose output
    verbose: bool = Field(default=False)


# Global config instance
config = AppConfig()


def get_config() -> AppConfig:
    """Get the global configuration instance"""
    return config


def update_config(**kwargs) -> AppConfig:
    """Update configuration with new values"""
    global config
    config = AppConfig(**{**config.model_dump(), **kwargs})
    return config