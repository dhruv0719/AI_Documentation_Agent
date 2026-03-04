# core/config.py
"""Configuration management for Code Documentation Agent."""

import os
import json
from pathlib import Path
from typing import Optional
from models.config_models import (
    Config, LLMConfig, ScannerConfig, 
    OutputConfig, ChangeDetectionConfig
    )

class ConfigManager:
    """Manages loading, saving, and accessing configuration."""
    
    def __init__(self):
        self._config: Optional[Config] = None
    
    def load_from_file(self, config_path: Path) -> Config:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to config file (JSON or YAML)
            
        Returns:
            Loaded Config instance
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        # Determine file type
        if config_path.suffix in ['.yaml', '.yml']:
            return self._load_yaml(config_path)
        elif config_path.suffix == '.json':
            return self._load_json(config_path)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")
    
    def _load_json(self, path: Path) -> Config:
        """Load config from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return self._deserialize(data)
    
    def _load_yaml(self, path: Path) -> Config:
        """Load config from YAML file."""
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for YAML config files. Install with: pip install pyyaml")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return self._deserialize(data)
    
    def _deserialize(self, data: dict) -> Config:
        """Convert dict to Config instance."""
        llm_data = data.get("llm", {})
        scanner_data = data.get("scanner", {})
        output_data = data.get("output", {})
        change_data = data.get("change_detection", {})
        
        # Build LLMConfig - matching actual dataclass fields!
        llm_config = LLMConfig(
            provider=llm_data.get("provider", "groq"),
            temperature=llm_data.get("temperature", 0.2),
            max_tokens=llm_data.get("max_tokens", 2500),
            small_model=llm_data.get("small_model", "qwen/qwen3-32b"),
            medium_model=llm_data.get("medium_model", "openai/gpt-oss-20b"),
            large_model=llm_data.get("large_model", "llama-3.3-70b-versatile"),
            synthesis_model=llm_data.get("synthesis_model", "llama-3.3-70b-versatile"),
        )
        # api_key set by __post_init__ from env
        
        # Build ScannerConfig
        scanner_defaults = ScannerConfig()
        scanner_config = ScannerConfig(
            ignore_dirs=scanner_data.get("ignore_dirs", scanner_defaults.ignore_dirs),
            include_extensions=scanner_data.get("include_extensions", [".py"]),
            max_file_size_bytes=scanner_data.get("max_file_size_bytes", 100_000),
        )
        
        # Build OutputConfig
        output_config = OutputConfig(
            output_dir=Path(output_data.get("output_dir", "./docs_output")),
            readme_filename=output_data.get("readme_filename", "README.md"),
            technical_filename=output_data.get("technical_filename", "TECHNICAL_DOC.md"),
            api_reference_filename=output_data.get("api_reference_filename", "API_REFERENCE.md"),
            include_timestamp=output_data.get("include_timestamp", True),
        )
        
        # Build ChangeDetectionConfig
        change_config = ChangeDetectionConfig(
            enabled=change_data.get("enabled", True),
            metadata_dir=Path(change_data.get("metadata_dir", ".docagent")),
            force_reanalysis=change_data.get("force_reanalysis", False),
        )
        
        return Config(
            llm=llm_config,
            scanner=scanner_config,
            output=output_config,
            change_detection=change_config,
            project_name=data.get("project_name"),
            log_level=data.get("log_level", "INFO"),
            verbose=data.get("verbose", False),
            enable_dependency_graph=data.get("enable_dependency_graph", False),
            enable_quality_metrics=data.get("enable_quality_metrics", False),
        )
    
    def _serialize(self, config: Config) -> dict:
        """Convert Config instance to dict."""
        return {
            "llm": {
                "provider": config.llm.provider,
                "small_model": config.llm.small_model,
                "medium_model": config.llm.medium_model,
                "large_model": config.llm.large_model,
                "synthesis_model": config.llm.synthesis_model,
                "temperature": config.llm.temperature,
                "max_tokens": config.llm.max_tokens,
                # NOTE: Never serialize api_key!
            },
            "scanner": {
                "ignore_dirs": config.scanner.ignore_dirs,
                "include_extensions": config.scanner.include_extensions,
                "max_file_size_bytes": config.scanner.max_file_size_bytes,
            },
            "output": {
                "output_dir": str(config.output.output_dir),
                "readme_filename": config.output.readme_filename,
                "technical_filename": config.output.technical_filename,
                "api_reference_filename": config.output.api_reference_filename,
                "include_timestamp": config.output.include_timestamp,
            },
            "change_detection": {
                "enabled": config.change_detection.enabled,
                "metadata_dir": str(config.change_detection.metadata_dir),
                "force_reanalysis": config.change_detection.force_reanalysis,
            },
            "project_name": config.project_name,
            "log_level": config.log_level,
            "verbose": config.verbose,
            "enable_dependency_graph": config.enable_dependency_graph,
            "enable_quality_metrics": config.enable_quality_metrics,
        }
    
    def save_to_file(self, config: Config, output_path: Path):
        """Save configuration to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = self._serialize(config)
        
        if output_path.suffix in ['.yaml', '.yml']:
            self._save_yaml(data, output_path)
        else:
            self._save_json(data, output_path)
    
    def _save_json(self, data: dict, path: Path):
        """Save config as JSON."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _save_yaml(self, data: dict, path: Path):
        """Save config as YAML."""
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for YAML config files. Install with: pip install pyyaml")
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def get_default_config(self) -> Config:
        """Get default configuration."""
        return Config()
    
    def find_config_file(self, start_dir: Path) -> Optional[Path]:
        """
        Search for config file in current directory and parents.
        
        Args:
            start_dir: Directory to start searching from
            
        Returns:
            Path to config file if found, None otherwise
        """
        current = start_dir.resolve()
        
        # Check up to 5 parent directories
        for _ in range(5):
            for ext in ['.yaml', '.yml', '.json']:
                config_path = current / f".docagent{ext}"
                if config_path.exists():
                    return config_path
            
            # Move to parent
            parent = current.parent
            if parent == current:  # Reached root
                break
            current = parent
        
        return None

# Global config manager instance
_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get global config manager instance."""
    global _manager
    if _manager is None:
        _manager = ConfigManager()
    return _manager


def load_config(config_path: Optional[Path] = None, project_root: Optional[Path] = None) -> Config:
    """
    Load configuration with smart defaults.
    
    Args:
        config_path: Explicit path to config file
        project_root: Project root to search for config
        
    Returns:
        Config instance
    """
    manager = get_config_manager()
    
    # If explicit path provided, use it
    if config_path:
        return manager.load_from_file(config_path)
    
    # Otherwise, search for config file
    search_dir = project_root or Path.cwd()
    found = manager.find_config_file(search_dir)
    
    if found:
        print(f"✓ Using config: {found}")
        return manager.load_from_file(found)
    
    # Fall back to defaults
    print("✓ Using default configuration")
    return manager.get_default_config()