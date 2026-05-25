# DocAgent - API Reference

> 📖 Complete API Documentation | Generated: 2026-04-12

## Table of Contents

- [analyzer](#analyzer)
  - [class CodeAnalyzer](#codeanalyzer)
- [dependency_analyzer](#dependency-analyzer)
  - [class DependencyAnalyzer](#dependencyanalyzer)
- [llm_provider](#llm-provider)
  - [class BaseLLMProvider](#basellmprovider)
- [provider_factory](#provider-factory)
- [__init__](#--init--)
- [groq_provider](#groq-provider)
  - [class GroqProvider](#groqprovider)
- [openai_provider](#openai-provider)
  - [class OpenAIProvider](#openaiprovider)
- [quality_analyzer](#quality-analyzer)
- [commands](#commands)
- [main](#main)
- [change_detector](#change-detector)
  - [class ChangeDetector](#changedetector)
- [config](#config)
  - [class ConfigManager](#configmanager)
- [hasher](#hasher)
  - [class FileHasher](#filehasher)
- [metadata_store](#metadata-store)
  - [class MetadataStore](#metadatastore)
- [scanner](#scanner)
- [enhanced_generator](#enhanced-generator)
  - [class EnhancedDocumentationGenerator](#enhanceddocumentationgenerator)
  - [class DocumentationGenerator](#documentationgenerator)
- [generator](#generator)
  - [class DocumentationGenerator](#documentationgenerator)
- [graphviz](#graphviz)
- [mermaid](#mermaid)
  - [class MermaidGenerator](#mermaidgenerator)
- [action](#action)
- [main](#main)
- [main_v2](#main-v2)
- [change_report](#change-report)
  - [class ChangeReport](#changereport)
- [config_models](#config-models)
  - [class LLMConfig](#llmconfig)
  - [class ScannerConfig](#scannerconfig)
  - [class OutputConfig](#outputconfig)
  - [class ChangeDetectionConfig](#changedetectionconfig)
  - [class Config](#config)
- [dependency_graph](#dependency-graph)
  - [class ModuleNode](#modulenode)
  - [class CircularDependency](#circulardependency)
  - [class DependencyGraph](#dependencygraph)
- [generation_result](#generation-result)
  - [class GenerationResult](#generationresult)
- [llm_models](#llm-models)
  - [class LLMResponse](#llmresponse)
  - [class LLMProviderError](#llmprovidererror)
  - [class RateLimitError](#ratelimiterror)
  - [class AuthenticationError](#authenticationerror)
  - [class ModelNotFoundError](#modelnotfounderror)
- [metadata](#metadata)
  - [class FileMetadata](#filemetadata)
  - [class ProjectMetadata](#projectmetadata)
- [parsed_file](#parsed-file)
  - [class ParameterInfo](#parameterinfo)
  - [class FunctionInfo](#functioninfo)
  - [class ClassInfo](#classinfo)
  - [class ImportInfo](#importinfo)
  - [class ParsedFile](#parsedfile)
  - [class ModuleSummary](#modulesummary)
  - [class ProjectAnalysis](#projectanalysis)
- [scan_result](#scan-result)
  - [class FileNode](#filenode)
  - [class DirectoryNode](#directorynode)
  - [class ScanResult](#scanresult)
- [base_parser](#base-parser)
  - [class BaseParser](#baseparser)
- [javascript_parser](#javascript-parser)
- [parser_factory](#parser-factory)
  - [class ParserFactory](#parserfactory)
- [python_parser](#python-parser)
  - [class PythonParser](#pythonparser)
- [typescript_parser](#typescript-parser)
- [test_change_detection](#test-change-detection)

---

## analyzer

**File:** `analysis\analyzer.py`

**Description:**

Code analyzer using LLM for understanding and documentation.

**Purpose:**

Analyzes code modules using language models to generate documentation and project synthesis

### class `CodeAnalyzer`

```python
class CodeAnalyzer:
```

Analyzes code using LLM to generate summaries and insights.

Supports both sync and async operation for flexibility.

#### Methods

##### `__init__`

```python
def __init__(self, provider: str = 'groq', api_key: Optional[str] = None, temperature: float = 0.2, max_tokens: int = 2500)
```

Initialize analyzer.

Args:
    provider: LLM provider ("groq" or "openai")
    api_key: API key (optional, reads from env)
    temperature: LLM temperature
    max_tokens: Max tokens per request

**Parameters:**

- **provider** (`str`, default=`'groq'`)
- **api_key** (`Optional[str]`, default=`None`)
- **temperature** (`float`, default=`0.2`)
- **max_tokens** (`int`, default=`2500`)

##### `from_config`

```python
def from_config(cls, llm_config: LLMConfig) -> 'CodeAnalyzer'
```

Create analyzer from LLMConfig.

**Parameters:**

- **llm_config** (`LLMConfig`)

**Returns:**

`'CodeAnalyzer'`

##### `analyze_module`

```python
def analyze_module(self, parsed_file: ParsedFile) -> ModuleSummary
```

Analyze a single module synchronously.

**Parameters:**

- **parsed_file** (`ParsedFile`)

**Returns:**

`ModuleSummary`

##### `synthesize_project`

```python
def synthesize_project(self, module_summaries: List[ModuleSummary], project_path: str) -> ProjectAnalysis
```

Synthesize project-level understanding synchronously.

**Parameters:**

- **module_summaries** (`List[ModuleSummary]`)
- **project_path** (`str`)

**Returns:**

`ProjectAnalysis`

##### `analyze_module_async`

```python
async def analyze_module_async(self, parsed_file: ParsedFile) -> ModuleSummary
```

Analyze a single module asynchronously.

**Parameters:**

- **parsed_file** (`ParsedFile`)

**Returns:**

`ModuleSummary`

##### `analyze_modules_async`

```python
async def analyze_modules_async(self, parsed_files: List[ParsedFile], max_concurrent: int = 5) -> List[ModuleSummary]
```

Analyze multiple modules concurrently.

Args:
    parsed_files: Files to analyze
    max_concurrent: Max concurrent API calls (rate limit protection)
    
Returns:
    List of ModuleSummary in same order as input

**Parameters:**

- **parsed_files** (`List[ParsedFile]`)
- **max_concurrent** (`int`, default=`5`)

**Returns:**

`List[ModuleSummary]`

##### `_build_module_prompt`

```python
def _build_module_prompt(self, parsed_file: ParsedFile) -> str
```

Build prompt for module analysis.

**Parameters:**

- **parsed_file** (`ParsedFile`)

**Returns:**

`str`

##### `_build_synthesis_prompt`

```python
def _build_synthesis_prompt(self, module_summaries: List[ModuleSummary], project_path: str) -> str
```

Build prompt for project synthesis.

**Parameters:**

- **module_summaries** (`List[ModuleSummary]`)
- **project_path** (`str`)

**Returns:**

`str`

##### `_parse_module_response`

```python
def _parse_module_response(self, response: str, parsed_file: ParsedFile) -> ModuleSummary
```

Parse LLM response into ModuleSummary.

**Parameters:**

- **response** (`str`)
- **parsed_file** (`ParsedFile`)

**Returns:**

`ModuleSummary`

##### `_parse_synthesis_response`

```python
def _parse_synthesis_response(self, response: str) -> ProjectAnalysis
```

Parse LLM response into ProjectAnalysis.

**Parameters:**

- **response** (`str`)

**Returns:**

`ProjectAnalysis`

##### `_clean_llm_response`

```python
def _clean_llm_response(self, response: str) -> str
```

Clean LLM response for JSON parsing.

**Parameters:**

- **response** (`str`)

**Returns:**

`str`

##### `_select_model_size`

```python
def _select_model_size(self, parsed_file: ParsedFile) -> str
```

Select model size based on file complexity.

**Parameters:**

- **parsed_file** (`ParsedFile`)

**Returns:**

`str`

##### `_empty_summary`

```python
def _empty_summary(self, parsed_file: ParsedFile) -> ModuleSummary
```

**Parameters:**

- **parsed_file** (`ParsedFile`)

**Returns:**

`ModuleSummary`

##### `_empty_project_analysis`

```python
def _empty_project_analysis(self) -> ProjectAnalysis
```

**Returns:**

`ProjectAnalysis`

---

## dependency_analyzer

**File:** `analysis\dependency_analyzer.py`

**Description:**

Builds a graph of how modules import each other. This help understand Project flow, Module importance, Circular dependencies, Analysis order

**Purpose:**

Analyzes Python project dependencies to build a graph showing module relationships, helping identify circular dependencies and module importance.

### class `DependencyAnalyzer`

```python
class DependencyAnalyzer:
```

Analyzes dependencies between project modules.

#### Methods

##### `__init__`

```python
def __init__(self, project_root: str, parsed_files: List[ParsedFile])
```

Initialize dependency analyzer.

Args:
    project_root: Root directory of the project
    parsed_files: List of parsed Python files

**Parameters:**

- **project_root** (`str`)
- **parsed_files** (`List[ParsedFile]`)

##### `build_graph`

```python
def build_graph(self) -> DependencyGraph
```

Build the complete dependency graph.

Returns:
    DependencyGraph with all modules and relationships

**Returns:**

`DependencyGraph`

##### `_create_nodes`

```python
def _create_nodes(self, graph: DependencyGraph)
```

Create nodes for all parsed files.

**Parameters:**

- **graph** (`DependencyGraph`)

##### `_build_reverse_dependencies`

```python
def _build_reverse_dependencies(self, graph: DependencyGraph)
```

Build imported_by relationships.

**Parameters:**

- **graph** (`DependencyGraph`)

##### `_calculate_depths`

```python
def _calculate_depths(self, graph: DependencyGraph)
```

Calculate depth of each node from entry points using BFS.

**Parameters:**

- **graph** (`DependencyGraph`)

##### `_detect_cycles`

```python
def _detect_cycles(self, graph: DependencyGraph)
```

Detect circular dependencies using DFS.

**Parameters:**

- **graph** (`DependencyGraph`)

##### `_build_module_mapping`

```python
def _build_module_mapping(self)
```

Build mapping from module names to file paths.

##### `_extract_import_name`

```python
def _extract_import_name(self, imp) -> str
```

Extract import name from ImportInfo object or string.

**Parameters:**

- **imp** (`Any`)

**Returns:**

`str`

##### `_is_entry_point`

```python
def _is_entry_point(self, parsed_file: ParsedFile) -> bool
```

Check if file is an entry point.

**Parameters:**

- **parsed_file** (`ParsedFile`)

**Returns:**

`bool`

##### `_is_internal_import`

```python
def _is_internal_import(self, import_name: str) -> bool
```

Check if import is from within the project.

**Parameters:**

- **import_name** (`str`)

**Returns:**

`bool`

##### `_resolve_import`

```python
def _resolve_import(self, import_name: str) -> Optional[str]
```

Resolve import name to file path.

**Parameters:**

- **import_name** (`str`)

**Returns:**

`Optional[str]`

##### `generate_summary`

```python
def generate_summary(self, graph: DependencyGraph) -> str
```

Generate text summary of dependency analysis.

Args:
    graph: DependencyGraph to summarize
    
Returns:
    Multi-line string with summary

**Parameters:**

- **graph** (`DependencyGraph`)

**Returns:**

`str`

##### `generate_mermaid`

```python
def generate_mermaid(self, graph: DependencyGraph, max_nodes: int = 50) -> str
```

Generate Mermaid diagram syntax.

Args:
    graph: DependencyGraph to visualize
    max_nodes: Maximum nodes to include (prevents huge diagrams)
    
Returns:
    Mermaid diagram syntax

**Parameters:**

- **graph** (`DependencyGraph`)
- **max_nodes** (`int`, default=`50`)

**Returns:**

`str`

##### `_sanitize_for_mermaid`

```python
def _sanitize_for_mermaid(self, name: str) -> str
```

Sanitize module name for Mermaid syntax.

**Parameters:**

- **name** (`str`)

**Returns:**

`str`

---

## llm_provider

**File:** `analysis\llm_provider.py`

**Description:**

Abstract interface for LLM providers.

**Purpose:**

Provides an abstract interface for LLM providers with synchronous and asynchronous generation capabilities.

### class `BaseLLMProvider`

```python
class BaseLLMProvider(ABC):
```

Abstract base class for LLM providers.

All LLM providers (Groq, OpenAI, Anthropic, etc.) must implement this interface.

#### Methods

##### `generate`

```python
async def generate(self, prompt: str, model: str = None, system_prompt: str = None) -> LLMResponse
```

Generate response from LLM (async).

Args:
    prompt: The prompt to send to the LLM
    model: Specific model to use (optional, uses default if not provided)
    
Returns:
    LLMResponse with generated content and metadata
    
Raises:
    LLMProviderError: If API call fails

**Parameters:**

- **prompt** (`str`)
- **model** (`str`, default=`None`)
- **system_prompt** (`str`, default=`None`)

**Returns:**

`LLMResponse`

##### `generate_sync`

```python
def generate_sync(self, prompt: str, model: str = None, system_prompt: str = None) -> LLMResponse
```

Generate response from LLM (synchronous).

Args:
    prompt: The prompt to send to the LLM
    model: Specific model to use (optional)
    
Returns:
    LLMResponse with generated content and metadata

**Parameters:**

- **prompt** (`str`)
- **model** (`str`, default=`None`)
- **system_prompt** (`str`, default=`None`)

**Returns:**

`LLMResponse`

##### `generate_with_retry`

```python
async def generate_with_retry(self, prompt: str, model: str = None, system_prompt: str = None, max_retries: int = None) -> LLMResponse
```

Generate with automatic retry on failure.

Retries on:
- Rate limit errors (with exponential backoff)
- Temporary API errors

Does NOT retry on:
- Authentication errors
- Invalid model errors

**Parameters:**

- **prompt** (`str`)
- **model** (`str`, default=`None`)
- **system_prompt** (`str`, default=`None`)
- **max_retries** (`int`, default=`None`)

**Returns:**

`LLMResponse`

##### `generate_sync_with_retry`

```python
def generate_sync_with_retry(self, prompt: str, model: str = None, system_prompt: str = None, max_retries: int = None) -> LLMResponse
```

Sync version of generate_with_retry.

**Parameters:**

- **prompt** (`str`)
- **model** (`str`, default=`None`)
- **system_prompt** (`str`, default=`None`)
- **max_retries** (`int`, default=`None`)

**Returns:**

`LLMResponse`

##### `get_model`

```python
def get_model(self, size: str = 'medium') -> str
```

Get model name by size category.

**Parameters:**

- **size** (`str`, default=`'medium'`)

**Returns:**

`str`

---

## provider_factory

**File:** `analysis\provider_factory.py`

**Description:**

Factory for creating LLM providers.

**Purpose:**

Factory module for instantiating LLM providers based on configuration or direct parameters.

### Functions

##### `get_llm_provider`

```python
def get_llm_provider(provider: str = 'groq', api_key: Optional[str] = None, temperature: float = 0.2, max_tokens: int = 2500, config: Optional[LLMConfig] = None) -> BaseLLMProvider
```

Factory function to create LLM provider.

Args:
    provider: Provider name
    api_key: API key
    temperature: Sampling temperature
    max_tokens: Max tokens
    config: Optional LLMConfig for model overrides

**Parameters:**

- **provider** (`str`, default=`'groq'`)
- **api_key** (`Optional[str]`, default=`None`)
- **temperature** (`float`, default=`0.2`)
- **max_tokens** (`int`, default=`2500`)
- **config** (`Optional[LLMConfig]`, default=`None`)

**Returns:**

`BaseLLMProvider`

##### `get_llm_provider_from_config`

```python
def get_llm_provider_from_config(config: LLMConfig) -> BaseLLMProvider
```

Create provider directly from config.

This is the preferred way when you have a Config object.

**Parameters:**

- **config** (`LLMConfig`)

**Returns:**

`BaseLLMProvider`

---

## __init__

**File:** `analysis\providers\__init__.py`

**Description:**

LLM provider implementations.

**Purpose:**

Serves as an entry point for LLM provider implementations, grouping related modules under the providers package.

---

## groq_provider

**File:** `analysis\providers\groq_provider.py`

**Description:**

Groq LLM provider implementation.

**Purpose:**

Provides integration with Groq's LLM API for asynchronous and synchronous text generation

### class `GroqProvider`

```python
class GroqProvider(BaseLLMProvider):
```

Groq API provider implementation.

#### Methods

##### `__init__`

```python
def __init__(self, api_key: Optional[str] = None, temperature: float = 0.2, max_tokens: int = 2500)
```

Initialize Groq provider.

Args:
    api_key: Groq API key (reads from GROQ_API_KEY env var if not provided)
    temperature: Sampling temperature (0.0 - 1.0)
    max_tokens: Maximum tokens to generate

**Parameters:**

- **api_key** (`Optional[str]`, default=`None`)
- **temperature** (`float`, default=`0.2`)
- **max_tokens** (`int`, default=`2500`)

##### `_build_messages`

```python
def _build_messages(self, prompt: str, system_prompt: str = None) -> list
```

Build message list with system prompt.

**Parameters:**

- **prompt** (`str`)
- **system_prompt** (`str`, default=`None`)

**Returns:**

`list`

##### `generate`

```python
async def generate(self, prompt: str, model: str = None, system_prompt: str = None) -> LLMResponse
```

Generate response asynchronously.

**Parameters:**

- **prompt** (`str`)
- **model** (`str`, default=`None`)
- **system_prompt** (`str`, default=`None`)

**Returns:**

`LLMResponse`

##### `generate_sync`

```python
def generate_sync(self, prompt: str, model: str = None, system_prompt: str = None) -> LLMResponse
```

Generate response synchronously.

**Parameters:**

- **prompt** (`str`)
- **model** (`str`, default=`None`)
- **system_prompt** (`str`, default=`None`)

**Returns:**

`LLMResponse`

---

## openai_provider

**File:** `analysis\providers\openai_provider.py`

**Description:**

OpenAI LLM provider implementation.

**Purpose:**

Provides integration with OpenAI's language models for asynchronous and synchronous text generation.

### class `OpenAIProvider`

```python
class OpenAIProvider(BaseLLMProvider):
```

OpenAI API provider implementation.

#### Methods

##### `__init__`

```python
def __init__(self, api_key: Optional[str] = None, temperature: float = 0.2, max_tokens: int = 2500)
```

Initialize OpenAI provider.

**Parameters:**

- **api_key** (`Optional[str]`, default=`None`)
- **temperature** (`float`, default=`0.2`)
- **max_tokens** (`int`, default=`2500`)

##### `generate`

```python
async def generate(self, prompt: str, model: str = None) -> LLMResponse
```

Generate response asynchronously.

**Parameters:**

- **prompt** (`str`)
- **model** (`str`, default=`None`)

**Returns:**

`LLMResponse`

##### `generate_sync`

```python
def generate_sync(self, prompt: str, model: str = None) -> LLMResponse
```

Generate response synchronously.

**Parameters:**

- **prompt** (`str`)
- **model** (`str`, default=`None`)

**Returns:**

`LLMResponse`

---

## quality_analyzer

**File:** `analysis\quality_analyzer.py`

**Purpose:**

This module is intended for analyzing code quality metrics but currently contains no implemented functionality.

---

## commands

**File:** `cli\commands.py`

**Purpose:**

This module is intended to handle command-line interface (CLI) commands but currently contains no implemented functions or classes.

---

## main

**File:** `cli\main.py`

**Purpose:**

This module serves as the entry point for a command-line interface (CLI) application.

---

## change_detector

**File:** `core\change_detector.py`

**Purpose:**

Detects changes in files or data by comparing current state with cached metadata using hashing and metadata storage.

### class `ChangeDetector`

```python
class ChangeDetector:
```

Detects which files changed since last analysis.

#### Methods

##### `__init__`

```python
def __init__(self, project_root: str)
```

**Parameters:**

- **project_root** (`str`)

##### `detect_changes`

```python
def detect_changes(self, current_files: List[str]) -> ChangeReport
```

Compare current files against last analysis

Args:
    current_files: List of file paths from scanner
    
Returns:
    ChangeReport with categorized changes

**Parameters:**

- **current_files** (`List[str]`)

**Returns:**

`ChangeReport`

##### `get_cached_summary`

```python
def get_cached_summary(self, file_path: str) -> Optional[ModuleSummary]
```

Get cached analysis for unchanged file.

Args:
    file_path: Path to file
    
Returns:
    Cached ModuleSummary or None

**Parameters:**

- **file_path** (`str`)

**Returns:**

`Optional[ModuleSummary]`

##### `update_metadata`

```python
def update_metadata(self, analyzed_files: List[str], summaries: Dict[str, ModuleSummary], project_name: str)
```

Update metadata after analysis.

Args:
    analyzed_files: Files that were analyzed
    summaries: Map of file_path → ModuleSummary
    project_name: Name of project

**Parameters:**

- **analyzed_files** (`List[str]`)
- **summaries** (`Dict[str, ModuleSummary]`)
- **project_name** (`str`)

##### `reload_metadata`

```python
def reload_metadata(self)
```

Force re-read from disk (if external process modified it).

---

## config

**File:** `core\config.py`

**Description:**

Configuration management for Code Documentation Agent.

**Purpose:**

Manages configuration settings for the Code Documentation Agent, supporting JSON and YAML formats.

### class `ConfigManager`

```python
class ConfigManager:
```

Manages loading, saving, and accessing configuration.

#### Methods

##### `__init__`

```python
def __init__(self)
```

##### `load_from_file`

```python
def load_from_file(self, config_path: Path) -> Config
```

Load configuration from file.

Args:
    config_path: Path to config file (JSON or YAML)
    
Returns:
    Loaded Config instance

**Parameters:**

- **config_path** (`Path`)

**Returns:**

`Config`

##### `_load_json`

```python
def _load_json(self, path: Path) -> Config
```

Load config from JSON file.

**Parameters:**

- **path** (`Path`)

**Returns:**

`Config`

##### `_load_yaml`

```python
def _load_yaml(self, path: Path) -> Config
```

Load config from YAML file.

**Parameters:**

- **path** (`Path`)

**Returns:**

`Config`

##### `_deserialize`

```python
def _deserialize(self, data: dict) -> Config
```

Convert dict to Config instance.

**Parameters:**

- **data** (`dict`)

**Returns:**

`Config`

##### `_serialize`

```python
def _serialize(self, config: Config) -> dict
```

Convert Config instance to dict.

**Parameters:**

- **config** (`Config`)

**Returns:**

`dict`

##### `save_to_file`

```python
def save_to_file(self, config: Config, output_path: Path)
```

Save configuration to file.

**Parameters:**

- **config** (`Config`)
- **output_path** (`Path`)

##### `_save_json`

```python
def _save_json(self, data: dict, path: Path)
```

Save config as JSON.

**Parameters:**

- **data** (`dict`)
- **path** (`Path`)

##### `_save_yaml`

```python
def _save_yaml(self, data: dict, path: Path)
```

Save config as YAML.

**Parameters:**

- **data** (`dict`)
- **path** (`Path`)

##### `get_default_config`

```python
def get_default_config(self) -> Config
```

Get default configuration.

**Returns:**

`Config`

##### `find_config_file`

```python
def find_config_file(self, start_dir: Path) -> Optional[Path]
```

Search for config file in current directory and parents.

Args:
    start_dir: Directory to start searching from
    
Returns:
    Path to config file if found, None otherwise

**Parameters:**

- **start_dir** (`Path`)

**Returns:**

`Optional[Path]`

### Functions

##### `get_config_manager`

```python
def get_config_manager() -> ConfigManager
```

Get global config manager instance.

**Returns:**

`ConfigManager`

##### `load_config`

```python
def load_config(config_path: Optional[Path] = None, project_root: Optional[Path] = None) -> Config
```

Load configuration with smart defaults.

Args:
    config_path: Explicit path to config file
    project_root: Project root to search for config
    
Returns:
    Config instance

**Parameters:**

- **config_path** (`Optional[Path]`, default=`None`)
- **project_root** (`Optional[Path]`, default=`None`)

**Returns:**

`Config`

---

## hasher

**File:** `core\hasher.py`

**Description:**

This module provides utilities for hashing file contents to detect changes efficiently. It includes functions to generate hashes for individual files and batches of files, which can be used to compare against previous analyses and determine what has changed since the last run.

**Purpose:**

This module provides utilities for hashing file contents to detect changes efficiently.

### class `FileHasher`

```python
class FileHasher:
```

Fast, reliable file hashing.

#### Methods

##### `hash_file`

```python
def hash_file(file_path: str) -> str
```

Generate SHA-256 hash of file content.

Args:
    file_path: Path to file

Returns:
    Hexa string of hash (64 chars)

**Parameters:**

- **file_path** (`str`)

**Returns:**

`str`

##### `hash_files`

```python
def hash_files(file_paths: List[str]) -> Dict[str, str]
```

Hash multiple files efficiently.

Returns:
    Dict mapping file_path → hash

**Parameters:**

- **file_paths** (`List[str]`)

**Returns:**

`Dict[str, str]`

---

## metadata_store

**File:** `core\metadata_store.py`

**Description:**

This module manages the persistent storage of project metadata, including loading and saving metadata to disk. It provides a simple interface for the rest of the system to access and update metadata about files and projects, ensuring that change detection and analysis can be performed efficiently across runs.

**Purpose:**

Manages persistent storage and retrieval of project metadata, enabling efficient change detection and analysis across system runs.

### class `MetadataStore`

```python
class MetadataStore:
```

Persistent storage for project metadata.

#### Methods

##### `__init__`

```python
def __init__(self, project_root: str)
```

**Parameters:**

- **project_root** (`str`)

##### `load`

```python
def load(self) -> Optional[ProjectMetadata]
```

Load metadata from disk.

Returns:
    ProjectMetadata if exists, None if first run

**Returns:**

`Optional[ProjectMetadata]`

##### `save`

```python
def save(self, metadata: ProjectMetadata)
```

Save metadata to disk.

**Parameters:**

- **metadata** (`ProjectMetadata`)

##### `clear`

```python
def clear(self)
```

Delete metadata (force full reanalysis).

##### `exists`

```python
def exists(self) -> bool
```

Check if metadata file exists.

**Returns:**

`bool`

##### `last_updated`

```python
def last_updated(self) -> Optional[datetime]
```

Get last update time without loading full metadata.

**Returns:**

`Optional[datetime]`

---

## scanner

**File:** `core\scanner.py`

**Description:**

This module provides functionality to scan a project directory and return Python files with structural information.

**Purpose:**

Scans a project directory to identify Python files and extract their structural information.

### Functions

##### `scan_project`

```python
def scan_project(project_path: str, ignore_dirs: List[str] = None) -> List[str]
```

Scan a project directory and return all Python files.

Args:
    project_path: Path to the project root.
    ignore_dirs: Directories to ignore during scanning.

Returns:
    List of relative path to .py files in the project.

**Parameters:**

- **project_path** (`str`)
- **ignore_dirs** (`List[str]`, default=`None`)

**Returns:**

`List[str]`

##### `scan_project_with_tree`

```python
def scan_project_with_tree(project_path: str, ignore_dirs: List[str] = None) -> ScanResult
```

Scan project and return detailed structure with tree and metadata.

Args:
    project_path: Path to the project root
    ignore_dirs: Directories to ignore during scanning
    
Returns:
    ScanResult with tree structure, file list, and metadata

**Parameters:**

- **project_path** (`str`)
- **ignore_dirs** (`List[str]`, default=`None`)

**Returns:**

`ScanResult`

##### `_check_entry_point`

```python
def _check_entry_point(file_path: Path) -> bool
```

Check if file has if __name__ == '__main__'.

**Parameters:**

- **file_path** (`Path`)

**Returns:**

`bool`

---

## enhanced_generator

**File:** `generation\enhanced_generator.py`

**Description:**

Enhanced Documentation Generator

Generates comprehensive documentation using:
1. ParsedFile - Actual code structure (functions, classes, signatures)
2. ModuleSummary - LLM-generated insights (purpose, responsibilities)
3. ProjectAnalysis - High-level project understanding
4. DependencyGraph - Module relationships (optional)

Output:
- README.md - Overview documentation
- TECHNICAL_DOC.md - Detailed technical reference
- API_REFERENCE.md - Complete API documentation

**Purpose:**

Generates comprehensive documentation for Python projects using parsed code structure and LLM-generated insights, producing README, technical documentation, and API reference files.

### class `EnhancedDocumentationGenerator`

```python
class EnhancedDocumentationGenerator:
```

Generates comprehensive markdown documentation.

Unlike the basic generator, this one:
- Includes actual function signatures and parameters
- Documents all classes with their methods
- Generates API reference with full details
- Adds Table of Contents
- Includes dependency diagrams (if mermaid available)

#### Methods

##### `__init__`

```python
def __init__(self, output_dir: str = 'docs')
```

Initialize the generator.

Args:
    output_dir: Directory for generated documentation

**Parameters:**

- **output_dir** (`str`, default=`'docs'`)

##### `generate_all`

```python
def generate_all(self, project_analysis: ProjectAnalysis, module_summaries: List[ModuleSummary], parsed_files: List[ParsedFile], project_name: str, dependency_diagram: Optional[str] = None, project_tree: Optional[str] = None) -> GenerationResult
```

Generate all documentation files.

Args:
    project_analysis: High-level project analysis
    module_summaries: LLM-generated module summaries
    parsed_files: Parsed code structure
    project_name: Name of the project
    dependency_diagram: Optional Mermaid diagram string

Returns:
    GenerationResult with paths to generated files

**Parameters:**

- **project_analysis** (`ProjectAnalysis`)
- **module_summaries** (`List[ModuleSummary]`)
- **parsed_files** (`List[ParsedFile]`)
- **project_name** (`str`)
- **dependency_diagram** (`Optional[str]`, default=`None`)
- **project_tree** (`Optional[str]`, default=`None`)

**Returns:**

`GenerationResult`

##### `_generate_readme`

```python
def _generate_readme(self, project_analysis: ProjectAnalysis, project_name: str, dependency_diagram: Optional[str] = None, project_tree: Optional[str] = None) -> Path
```

Generate README.md

**Parameters:**

- **project_analysis** (`ProjectAnalysis`)
- **project_name** (`str`)
- **dependency_diagram** (`Optional[str]`, default=`None`)
- **project_tree** (`Optional[str]`, default=`None`)

**Returns:**

`Path`

##### `_generate_technical_doc`

```python
def _generate_technical_doc(self, project_analysis: ProjectAnalysis, module_summaries: List[ModuleSummary], parsed_files: List[ParsedFile], summary_lookup: Dict[str, ModuleSummary], project_name: str) -> Path
```

Generate TECHNICAL_DOC.md

**Parameters:**

- **project_analysis** (`ProjectAnalysis`)
- **module_summaries** (`List[ModuleSummary]`)
- **parsed_files** (`List[ParsedFile]`)
- **summary_lookup** (`Dict[str, ModuleSummary]`)
- **project_name** (`str`)

**Returns:**

`Path`

##### `_format_module_detailed`

```python
def _format_module_detailed(self, parsed_file: ParsedFile, summary: Optional[ModuleSummary]) -> List[str]
```

Format detailed documentation for a single module.

**Parameters:**

- **parsed_file** (`ParsedFile`)
- **summary** (`Optional[ModuleSummary]`)

**Returns:**

`List[str]`

##### `_format_class`

```python
def _format_class(self, cls: ClassInfo) -> List[str]
```

Format a class for documentation.

**Returns:**

`List[str]`

##### `_format_function`

```python
def _format_function(self, func: FunctionInfo) -> List[str]
```

Format a function for documentation.

**Parameters:**

- **func** (`FunctionInfo`)

**Returns:**

`List[str]`

##### `_generate_api_reference`

```python
def _generate_api_reference(self, parsed_files: List[ParsedFile], summary_lookup: Dict[str, ModuleSummary], project_name: str) -> Path
```

Generate API_REFERENCE.md - complete API documentation.

**Parameters:**

- **parsed_files** (`List[ParsedFile]`)
- **summary_lookup** (`Dict[str, ModuleSummary]`)
- **project_name** (`str`)

**Returns:**

`Path`

##### `_format_api_module`

```python
def _format_api_module(self, parsed_file: ParsedFile, summary: Optional[ModuleSummary]) -> List[str]
```

Format complete API documentation for a module.

**Parameters:**

- **parsed_file** (`ParsedFile`)
- **summary** (`Optional[ModuleSummary]`)

**Returns:**

`List[str]`

##### `_format_api_class`

```python
def _format_api_class(self, cls: ClassInfo) -> List[str]
```

Format complete API documentation for a class.

**Returns:**

`List[str]`

##### `_format_api_function`

```python
def _format_api_function(self, func: FunctionInfo, is_method: bool = False) -> List[str]
```

Format complete API documentation for a function.

**Parameters:**

- **func** (`FunctionInfo`)
- **is_method** (`bool`, default=`False`)

**Returns:**

`List[str]`

### class `DocumentationGenerator`

```python
class DocumentationGenerator(EnhancedDocumentationGenerator):
```

Alias for backward compatibility.

---

## generator

**File:** `generation\generator.py`

**Description:**

This module generates markdown documentation from analysis results.

**Purpose:**

This module generates markdown documentation from analysis results, focusing on creating README and technical documentation files.

### class `DocumentationGenerator`

```python
class DocumentationGenerator:
```

Generates README and technical documentation from analysis results.

#### Methods

##### `__init__`

```python
def __init__(self, output_dir: str = 'output')
```

Initialize the documentation generator.

Args:
    output_dir: Directory to save generated documentation (default: 'output')

**Parameters:**

- **output_dir** (`str`, default=`'output'`)

##### `generate_readme`

```python
def generate_readme(self, project_analysis: ProjectAnalysis, project_name: str) -> str
```

Generate README.md (overview documentation).

Args:
    project_analysis: High-level project analysis from LLM
    project_name: Name of the project
    
Returns:
    Path to generated README.md file

**Parameters:**

- **project_analysis** (`ProjectAnalysis`)
- **project_name** (`str`)

**Returns:**

`str`

##### `generate_technical_doc`

```python
def generate_technical_doc(self, project_analysis: ProjectAnalysis, module_summaries: List[ModuleSummary], project_name: str) -> str
```

Generate TECHNICAL_DOC.md (detailed technical documentation).

Args:
    project_analysis: High-level project analysis from LLM
    module_summaries: List of all module summaries from LLM
    project_name: Name of the project
    
Returns:
    Path to generated TECHNICAL_DOC.md file

**Parameters:**

- **project_analysis** (`ProjectAnalysis`)
- **module_summaries** (`List[ModuleSummary]`)
- **project_name** (`str`)

**Returns:**

`str`

##### `generate_all`

```python
def generate_all(self, project_analysis: ProjectAnalysis, module_summaries: List[ModuleSummary], project_name: str) -> Dict[str, str]
```

Generate all documentation files (README and Technical Doc).

Args:
    project_analysis: High-level project analysis from LLM
    module_summaries: List of all module summaries from LLM
    project_name: Name of the project
    
Returns:
    Dictionary with paths to generated files:
    {
        'readme': 'path/to/README.md',
        'technical_doc': 'path/to/TECHNICAL_DOC.md'
    }

**Parameters:**

- **project_analysis** (`ProjectAnalysis`)
- **module_summaries** (`List[ModuleSummary]`)
- **project_name** (`str`)

**Returns:**

`Dict[str, str]`

##### `_build_readme_content`

```python
def _build_readme_content(self, project_analysis: ProjectAnalysis, project_name: str) -> str
```

Build README.md content string.

**Parameters:**

- **project_analysis** (`ProjectAnalysis`)
- **project_name** (`str`)

**Returns:**

`str`

##### `_build_technical_doc_content`

```python
def _build_technical_doc_content(self, project_analysis: ProjectAnalysis, module_summaries: List[ModuleSummary], project_name: str) -> str
```

Build TECHNICAL_DOC.md content string.

**Parameters:**

- **project_analysis** (`ProjectAnalysis`)
- **module_summaries** (`List[ModuleSummary]`)
- **project_name** (`str`)

**Returns:**

`str`

##### `_format_module_section`

```python
def _format_module_section(self, summary: ModuleSummary) -> str
```

Format a single module's documentation section.

**Parameters:**

- **summary** (`ModuleSummary`)

**Returns:**

`str`

---

## graphviz

**File:** `generation\visualizers\graphviz.py`

**Purpose:**

Provides integration with Graphviz for generating visual graphs and diagrams.

---

## mermaid

**File:** `generation\visualizers\mermaid.py`

**Description:**

Mermaid Diagram Generator

Generates Mermaid.js diagrams for:
- Module dependencies
- Class hierarchies
- Project architecture

**Purpose:**

Generates Mermaid.js diagrams for Python projects including class hierarchies, module dependencies, and architecture visualizations

### class `MermaidGenerator`

```python
class MermaidGenerator:
```

Generates Mermaid diagram code.

Mermaid diagrams can be rendered in:
- GitHub markdown (automatic)
- GitLab markdown (automatic)
- VS Code with extension
- https://mermaid.live

Usage:
    generator = MermaidGenerator()
    diagram = generator.dependency_diagram(parsed_files)
    
    # Include in markdown:
    # ```mermaid
    # {diagram}
    # ```

#### Methods

##### `__init__`

```python
def __init__(self)
```

##### `class_diagram`

```python
def class_diagram(self, classes: List, title: str = 'Class Diagram') -> str
```

Generate class relationship diagram.

Args:
    classes: List of ClassInfo objects
    title: Diagram title

Returns:
    Mermaid class diagram code

**Parameters:**

- **classes** (`List`)
- **title** (`str`, default=`'Class Diagram'`)

**Returns:**

`str`

##### `flowchart`

```python
def flowchart(self, steps: List[Dict], title: str = 'Flow') -> str
```

Generate a flowchart.

Args:
    steps: List of dicts with 'id', 'label', 'next' keys
    title: Diagram title

Returns:
    Mermaid flowchart code

**Parameters:**

- **steps** (`List[Dict]`)
- **title** (`str`, default=`'Flow'`)

**Returns:**

`str`

##### `architecture_diagram`

```python
def architecture_diagram(self, layers: Dict[str, List[str]]) -> str
```

Generate architecture layer diagram.

Args:
    layers: Dict mapping layer names to module names
            e.g., {"CLI": ["main.py"], "Core": ["scanner.py", "parser.py"]}

Returns:
    Mermaid diagram code

**Parameters:**

- **layers** (`Dict[str, List[str]]`)

**Returns:**

`str`

##### `_safe_id`

```python
def _safe_id(self, name: str) -> str
```

Convert name to safe Mermaid node ID.

**Parameters:**

- **name** (`str`)

**Returns:**

`str`

##### `wrap_for_markdown`

```python
def wrap_for_markdown(self, diagram: str) -> str
```

Wrap diagram in markdown code fence.

**Parameters:**

- **diagram** (`str`)

**Returns:**

`str`

### Functions

##### `generate_dependency_diagram`

```python
def generate_dependency_diagram(parsed_files: List) -> str
```

Quick function to generate dependency diagram.

**Parameters:**

- **parsed_files** (`List`)

**Returns:**

`str`

##### `generate_class_diagram`

```python
def generate_class_diagram(classes: List) -> str
```

Quick function to generate class diagram.

**Parameters:**

- **classes** (`List`)

**Returns:**

`str`

---

## action

**File:** `github\action.py`

**Purpose:**

This module currently contains no functions, classes, or implementations and serves as an empty namespace or placeholder.

---

## main

**File:** `main.py`

**Description:**

Main orchestrator for the Code Documentation Agent.

**Purpose:**

Main orchestrator for generating code documentation by coordinating parsing, analysis, and generation components.

### Functions

##### `generate_documentation`

```python
def generate_documentation(project_path: str, project_name: str = None)
```

Complete pipeline: Scan → Parse → Analyze → Generate Docs

Args:
    project_path: Path to the project root
    project_name: Name of the project (uses folder name if not provided)

**Parameters:**

- **project_path** (`str`)
- **project_name** (`str`, default=`None`)

---

## main_v2

**File:** `main_v2.py`

**Description:**

Code Documentation Agent V2 - Main Orchestrator

Pipeline:
  SCAN → CHANGE DETECT → PARSE → DEPENDENCY → LLM ANALYZE → GENERATE

Features:
  - Change detection (only re-analyze modified files)
  - Dependency graph analysis
  - Enhanced documentation with code details
  - Multiple LLM provider support
  - Configuration file support

**Purpose:**

Orchestrate a code documentation pipeline with change detection, dependency analysis, and LLM-powered documentation generation

### Functions

##### `generate_documentation`

```python
def generate_documentation(project_path: str, project_name: Optional[str] = None, force: bool = False, provider: str = 'groq', output_dir: Optional[str] = None)
```

Complete documentation generation pipeline.

Args:
    project_path: Path to project root
    project_name: Name of project (defaults to folder name)
    force: If True, ignore cache and reanalyze everything
    provider: LLM provider ("groq" or "openai")
    output_dir: Output directory (defaults to output/{project_name})

**Parameters:**

- **project_path** (`str`)
- **project_name** (`Optional[str]`, default=`None`)
- **force** (`bool`, default=`False`)
- **provider** (`str`, default=`'groq'`)
- **output_dir** (`Optional[str]`, default=`None`)

---

## change_report

**File:** `models\change_report.py`

**Description:**

This module defines the ChangeReport data model, which captures the differences between the current state of a project and its previous analysis. It identifies added, modified, deleted, and unchanged files to determine what needs to be re-analyzed.

**Purpose:**

Captures differences between project states to determine which files require re-analysis

### class `ChangeReport`

```python
class ChangeReport:
```

Report of what changed since last analysis.

#### Methods

##### `has_changes`

```python
def has_changes(self) -> bool
```

Check if there are any changes.

**Returns:**

`bool`

##### `files_to_analyze`

```python
def files_to_analyze(self) -> List[str]
```

List of files that need analysis (added or modified).

**Returns:**

`List[str]`

##### `summary`

```python
def summary(self) -> str
```

Human-readable summary of changes

**Returns:**

`str`

##### `__str__`

```python
def __str__(self) -> str
```

**Returns:**

`str`

---

## config_models

**File:** `models\config_models.py`

**Description:**

Data models for configuration settings.

**Purpose:**

Defines data models for application configuration, including LLM, scanner, output, and change detection settings, and provides mechanisms to validate and instantiate components.

### class `LLMConfig`

```python
class LLMConfig:
```

LLM provider configuration.

#### Methods

##### `__post_init__`

```python
def __post_init__(self)
```

##### `get_model`

```python
def get_model(self, size: str = 'medium') -> str
```

Get model name by size category.

Args:
    size: "small", "medium", or "large"
    
Returns:
    Model name string

**Parameters:**

- **size** (`str`, default=`'medium'`)

**Returns:**

`str`

### class `ScannerConfig`

```python
class ScannerConfig:
```

Scanner configuration.

### class `OutputConfig`

```python
class OutputConfig:
```

Output configuration.

### class `ChangeDetectionConfig`

```python
class ChangeDetectionConfig:
```

Change detection configuration.

### class `Config`

```python
class Config:
```

Main configuration container.

---

## dependency_graph

**File:** `models\dependency_graph.py`

**Description:**

Data models for module dependency analysis.

**Purpose:**

Models and analyzes dependencies between software modules, detecting relationships, coupling, and circular dependencies.

### class `ModuleNode`

```python
class ModuleNode:
```

Represents a module in the dependency graph.

#### Methods

##### `is_leaf`

```python
def is_leaf(self) -> bool
```

True if nothing imports this module.

**Returns:**

`bool`

##### `is_root`

```python
def is_root(self) -> bool
```

True if this module doesn't import any internal modules.

**Returns:**

`bool`

##### `coupling_score`

```python
def coupling_score(self) -> int
```

How coupled this module is (total connections).

**Returns:**

`int`

### class `CircularDependency`

```python
class CircularDependency:
```

Represents a circular dependency cycle.

#### Methods

##### `length`

```python
def length(self) -> int
```

Number of modules in the cycle

**Returns:**

`int`

##### `__str__`

```python
def __str__(self) -> str
```

Human-readable representation.

**Returns:**

`str`

### class `DependencyGraph`

```python
class DependencyGraph:
```

Graph of module dependencies.

This is a DATA model. All graph-building logic
lives in DependencyAnalyzer.

#### Methods

##### `total_modules`

```python
def total_modules(self) -> int
```

Total number of modules in the project.

**Returns:**

`int`

##### `root_modules`

```python
def root_modules(self) -> List[str]
```

Modules that don't import any internal modules (utility modules).

**Returns:**

`List[str]`

##### `leaf_modules`

```python
def leaf_modules(self) -> List[str]
```

Modules that nothing else imports (dead code candidates).

**Returns:**

`List[str]`

##### `most_imported`

```python
def most_imported(self) -> List[tuple]
```

Modules sorted by how many other modules import them.

Returns:
    List of (file_path, import_count) tuples, sorted by count descending

**Returns:**

`List[tuple]`

##### `most_coupled`

```python
def most_coupled(self) -> List[tuple]
```

Modules with highest coupling (most connections).

Returns:
    List of (file_path, coupling_score) tuples

**Returns:**

`List[tuple]`

##### `has_circular_dependencies`

```python
def has_circular_dependencies(self) -> bool
```

True if circular dependencies were detected.

**Returns:**

`bool`

##### `get_node`

```python
def get_node(self, file_path: str) -> Optional[ModuleNode]
```

Get a module node by file path.

**Parameters:**

- **file_path** (`str`)

**Returns:**

`Optional[ModuleNode]`

##### `get_dependencies`

```python
def get_dependencies(self, file_path: str) -> List[str]
```

Get all modules that the given file imports.

**Parameters:**

- **file_path** (`str`)

**Returns:**

`List[str]`

##### `get_dependents`

```python
def get_dependents(self, file_path: str) -> List[str]
```

Get all modules that import the given file.

**Parameters:**

- **file_path** (`str`)

**Returns:**

`List[str]`

##### `get_analysis_order`

```python
def get_analysis_order(self) -> List[str]
```

Get optimal analysis order (topological sort).

Analyze dependencies before dependents so when we
analyze a file, we already understand what it depends on.

**Returns:**

`List[str]`

##### `get_external_dependencies`

```python
def get_external_dependencies(self) -> List[str]
```

Get all unique external dependencies across the project.

**Returns:**

`List[str]`

##### `get_modules_at_depth`

```python
def get_modules_at_depth(self, depth: int) -> List[str]
```

Get all modules at a specific depth from entry points.

**Parameters:**

- **depth** (`int`)

**Returns:**

`List[str]`

---

## generation_result

**File:** `models\generation_result.py`

**Description:**

Data model for generation results.

**Purpose:**

Defines a data model to represent the results of a generation process, including metadata and output details.

### class `GenerationResult`

```python
class GenerationResult:
```

Result of documentation generation.

#### Methods

##### `summary`

```python
def summary(self) -> str
```

Human-readable generation summary.

**Returns:**

`str`

---

## llm_models

**File:** `models\llm_models.py`

**Description:**

Data models for LLM interactions.

**Purpose:**

Defines data structures and custom exception classes for interacting with language model providers.

### class `LLMResponse`

```python
class LLMResponse:
```

Standardized response from any LLM provider.

### class `LLMProviderError`

```python
class LLMProviderError(Exception):
```

Base error for LLM provider issues.

### class `RateLimitError`

```python
class RateLimitError(LLMProviderError):
```

API rate limit hit.

### class `AuthenticationError`

```python
class AuthenticationError(LLMProviderError):
```

Invalid API key.

### class `ModelNotFoundError`

```python
class ModelNotFoundError(LLMProviderError):
```

Requested model doesn't exist.

---

## metadata

**File:** `models\metadata.py`

**Description:**

This module defines data models for representing metadata about files and projects, including file hashes, last analysis timestamps, and summaries of file contents. This metadata is crucial for change detection and efficient re-analysis of only modified files.

**Purpose:**

This module defines data models for representing metadata about files and projects, including file hashes, last analysis timestamps, and summaries of file contents. This metadata is crucial for change detection and efficient re-analysis of only modified files.

### class `FileMetadata`

```python
class FileMetadata:
```

Metadata about a single file.

### class `ProjectMetadata`

```python
class ProjectMetadata:
```

Metadata for entire project.

#### Methods

##### `to_json`

```python
def to_json(self) -> Dict
```

Serialize to JSON for storage.

**Returns:**

`Dict`

##### `from_json`

```python
def from_json(data: Dict) -> 'ProjectMetadata'
```

Deserialize from JSON.

**Parameters:**

- **data** (`Dict`)

**Returns:**

`'ProjectMetadata'`

---

## parsed_file

**File:** `models\parsed_file.py`

**Description:**

This module defines data models for representing parsed information from Python files, including functions, classes, and modules. It also includes models for summarizing module and project-level insights after analysis.

**Purpose:**

Provides data models for representing parsed Python file elements and summarizing analysis at module and project levels.

### class `ParameterInfo`

```python
class ParameterInfo:
```

Detailed parameter information.

#### Methods

##### `__str__`

```python
def __str__(self) -> str
```

Format: name: type = default

**Returns:**

`str`

### class `FunctionInfo`

```python
class FunctionInfo:
```

Information about a function or method.

#### Methods

##### `signature`

```python
def signature(self) -> str
```

Generate readable signature.

**Returns:**

`str`

### class `ClassInfo`

```python
class ClassInfo:
```

Information about a class.

#### Methods

##### `is_dataclass`

```python
def is_dataclass(self) -> bool
```

**Returns:**

`bool`

### class `ImportInfo`

```python
class ImportInfo:
```

Structured import information.

#### Methods

##### `__str__`

```python
def __str__(self) -> str
```

**Returns:**

`str`

### class `ParsedFile`

```python
class ParsedFile:
```

Complete parsed information about a Python file.

#### Methods

##### `has_content`

```python
def has_content(self) -> bool
```

Check if file has meaningful content to document.

**Returns:**

`bool`

##### `module_name`

```python
def module_name(self) -> str
```

Extract module name from file path.

**Returns:**

`str`

### class `ModuleSummary`

```python
class ModuleSummary:
```

Summary of a single module after LLM analysis.

#### Methods

##### `to_dict`

```python
def to_dict(self) -> dict
```

Convert to dict for JSON serialization

**Returns:**

`dict`

##### `from_dict`

```python
def from_dict(data: dict) -> 'ModuleSummary'
```

Create ModuleSummary from dict

**Parameters:**

- **data** (`dict`)

**Returns:**

`'ModuleSummary'`

### class `ProjectAnalysis`

```python
class ProjectAnalysis:
```

High-level project understanding after synthesis.

---

## scan_result

**File:** `models\scan_result.py`

**Description:**

Data models for project scanning results, including file trees, directory structures, and scan metadata.

**Purpose:**

This module defines data models for representing and processing project scanning results, including file/directory structures and metadata.

### class `FileNode`

```python
class FileNode:
```

Represents a file in the project.

### class `DirectoryNode`

```python
class DirectoryNode:
```

Represents a directory in the project structure.

#### Methods

##### `to_tree_string`

```python
def to_tree_string(self, prefix: str = '', is_last: bool = True) -> str
```

Generate ASCII tree representation.

**Parameters:**

- **prefix** (`str`, default=`''`)
- **is_last** (`bool`, default=`True`)

**Returns:**

`str`

### class `ScanResult`

```python
class ScanResult:
```

Complete scan result with tree structure and metadata.

#### Methods

##### `total_size_mb`

```python
def total_size_mb(self) -> float
```

Total size in megabytes.

**Returns:**

`float`

##### `get_tree_string`

```python
def get_tree_string(self) -> str
```

Get ASCII tree representation of project structure.

**Returns:**

`str`

---

## base_parser

**File:** `parsers\base_parser.py`

**Description:**

Base parser interface for language-agnostic parsing.

**Purpose:**

Provides an abstract base class for language-agnostic file parsing interfaces.

### class `BaseParser`

```python
class BaseParser(ABC):
```

Abstract base class for all language parsers.

Each language (Python, JavaScript, etc.) implements this interface.
This allows the ParserFactory to work with any language uniformly.

#### Methods

##### `__init__`

```python
def __init__(self, project_root: Optional[str] = None)
```

**Parameters:**

- **project_root** (`Optional[str]`, default=`None`)

##### `parse_file`

```python
def parse_file(self, file_path: str) -> Optional[ParsedFile]
```

Parse a single file and extract structured information.

Args:
    file_path: Path to file (relative to project_root)

Returns:
    ParsedFile with extracted information, or None if failed

**Parameters:**

- **file_path** (`str`)

**Returns:**

`Optional[ParsedFile]`

##### `parse_files`

```python
def parse_files(self, file_paths: List[str]) -> List[ParsedFile]
```

Parse multiple files.

**Parameters:**

- **file_paths** (`List[str]`)

**Returns:**

`List[ParsedFile]`

##### `supported_extensions`

```python
def supported_extensions(self) -> List[str]
```

Return list of file extensions this parser handles.

**Returns:**

`List[str]`

---

## javascript_parser

**File:** `parsers\javascript_parser.py`

**Purpose:**

This module is intended for parsing JavaScript code but currently contains no code, imports, classes, or functions.

---

## parser_factory

**File:** `parsers\parser_factory.py`

**Description:**

Factory for creating appropriate parser based on file type.

**Purpose:**

Factory for creating appropriate parser based on file type.

### class `ParserFactory`

```python
class ParserFactory:
```

Factory to get the right parser for each file type.

Usage:
    factory = ParserFactory(project_root="/path/to/project")
    parser = factory.get_parser("main.py")
    parsed = parser.parse_file("main.py")

#### Methods

##### `__init__`

```python
def __init__(self, project_root: Optional[str] = None)
```

**Parameters:**

- **project_root** (`Optional[str]`, default=`None`)

##### `get_parser`

```python
def get_parser(self, file_path: str) -> Optional[BaseParser]
```

Get appropriate parser for a file.

Args:
    file_path: Path to the file

Returns:
    Parser instance or None if unsupported

**Parameters:**

- **file_path** (`str`)

**Returns:**

`Optional[BaseParser]`

##### `can_parse`

```python
def can_parse(self, file_path: str) -> bool
```

Check if we have a parser for this file type.

**Parameters:**

- **file_path** (`str`)

**Returns:**

`bool`

##### `register_parser`

```python
def register_parser(cls, extension: str, parser_class: Type[BaseParser])
```

Register a new parser for an extension.

**Parameters:**

- **extension** (`str`)
- **parser_class** (`Type[BaseParser]`)

##### `supported_extensions`

```python
def supported_extensions(self) -> list
```

List all supported extensions.

**Returns:**

`list`

---

## python_parser

**File:** `parsers\python_parser.py`

**Description:**

This module provides functionality to parse Python files and extract structured information about classes, functions, imports, and docstrings.

**Purpose:**

This module parses Python files to extract structured information about classes, functions, imports, and docstrings.

### class `PythonParser`

```python
class PythonParser:
```

Enhanced Python parser using AST.

Extracts:
- Classes with base classes, decorators, methods
- Functions with parameters, types, decorators
- Structured imports
- Global variables
- Entry point detection

#### Methods

##### `__init__`

```python
def __init__(self, project_root: Optional[str] = None)
```

**Parameters:**

- **project_root** (`Optional[str]`, default=`None`)

##### `parse_file`

```python
def parse_file(self, file_path: str) -> Optional[ParsedFile]
```

Parse a Python file and extract all information.

**Parameters:**

- **file_path** (`str`)

**Returns:**

`Optional[ParsedFile]`

##### `parse_files`

```python
def parse_files(self, file_paths: List[str]) -> List[ParsedFile]
```

Parse multiple files, skip failures.

**Parameters:**

- **file_paths** (`List[str]`)

**Returns:**

`List[ParsedFile]`

##### `_extract_imports`

```python
def _extract_imports(self, tree: ast.Module) -> List[ImportInfo]
```

Extract all imports with full details.

**Parameters:**

- **tree** (`ast.Module`)

**Returns:**

`List[ImportInfo]`

##### `_extract_classes`

```python
def _extract_classes(self, tree: ast.Module) -> List[ClassInfo]
```

Extract all class definitions.

**Parameters:**

- **tree** (`ast.Module`)

**Returns:**

`List[ClassInfo]`

##### `_parse_class`

```python
def _parse_class(self, node: ast.ClassDef) -> ClassInfo
```

Parse a single class definition.

**Parameters:**

- **node** (`ast.ClassDef`)

**Returns:**

`ClassInfo`

##### `_extract_functions`

```python
def _extract_functions(self, tree: ast.Module) -> List[FunctionInfo]
```

Extract top-level functions only.

**Parameters:**

- **tree** (`ast.Module`)

**Returns:**

`List[FunctionInfo]`

##### `_parse_function`

```python
def _parse_function(self, node) -> FunctionInfo
```

Parse a function or method definition.

**Parameters:**

- **node** (`Any`)

**Returns:**

`FunctionInfo`

##### `_extract_parameters`

```python
def _extract_parameters(self, args: ast.arguments) -> List[ParameterInfo]
```

Extract function parameters with types and defaults.

**Parameters:**

- **args** (`ast.arguments`)

**Returns:**

`List[ParameterInfo]`

##### `_extract_decorators`

```python
def _extract_decorators(self, node) -> List[str]
```

Extract decorator names from a function or class.

**Parameters:**

- **node** (`Any`)

**Returns:**

`List[str]`

##### `_extract_global_variables`

```python
def _extract_global_variables(self, tree: ast.Module) -> List[str]
```

Extract module-level variable assignments.

**Parameters:**

- **tree** (`ast.Module`)

**Returns:**

`List[str]`

##### `_check_entry_point`

```python
def _check_entry_point(self, tree: ast.Module) -> bool
```

Check if module has if __name__ == '__main__'.

**Parameters:**

- **tree** (`ast.Module`)

**Returns:**

`bool`

##### `_annotation_to_string`

```python
def _annotation_to_string(self, node) -> str
```

Convert type annotation to string.

**Parameters:**

- **node** (`Any`)

**Returns:**

`str`

##### `_node_to_string`

```python
def _node_to_string(self, node) -> str
```

Convert AST node to string representation.

**Parameters:**

- **node** (`Any`)

**Returns:**

`str`

##### `_get_attribute_name`

```python
def _get_attribute_name(self, node: ast.Attribute) -> str
```

Get full attribute name like 'module.Class'.

**Parameters:**

- **node** (`ast.Attribute`)

**Returns:**

`str`

### Functions

##### `parse_file`

```python
def parse_file(file_path: str, project_root: Optional[str] = None) -> Optional[ParsedFile]
```

Parse a single file (backward compatible).

**Parameters:**

- **file_path** (`str`)
- **project_root** (`Optional[str]`, default=`None`)

**Returns:**

`Optional[ParsedFile]`

---

## typescript_parser

**File:** `parsers\typescript_parser.py`

**Purpose:**

This module is intended to parse TypeScript code, though it currently contains no implemented functionality.

---

## test_change_detection

**File:** `test\test_change_detection.py`

**Purpose:**

This module contains a test case for verifying the functionality of the change detection system in the core module.

### Functions

##### `test_change_detection`

```python
def test_change_detection()
```

Test change detection on a real project.

---
