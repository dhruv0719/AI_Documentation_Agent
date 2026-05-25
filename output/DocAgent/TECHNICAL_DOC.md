# DocAgent - Technical Documentation

> 🔧 Developer Reference | Generated: 2026-04-12 14:19

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Design Patterns](#design-patterns)
- [Module Reference](#module-reference)
  - [analysis\analyzer.py](#analyzer)
  - [analysis\dependency_analyzer.py](#dependency-analyzer)
  - [analysis\llm_provider.py](#llm-provider)
  - [analysis\provider_factory.py](#provider-factory)
  - [analysis\providers\__init__.py](#--init--)
  - [analysis\providers\groq_provider.py](#groq-provider)
  - [analysis\providers\openai_provider.py](#openai-provider)
  - [analysis\quality_analyzer.py](#quality-analyzer)
  - [cli\commands.py](#commands)
  - [cli\main.py](#main)
  - [core\change_detector.py](#change-detector)
  - [core\config.py](#config)
  - [core\hasher.py](#hasher)
  - [core\metadata_store.py](#metadata-store)
  - [core\scanner.py](#scanner)
  - [generation\enhanced_generator.py](#enhanced-generator)
  - [generation\generator.py](#generator)
  - [generation\visualizers\graphviz.py](#graphviz)
  - [generation\visualizers\mermaid.py](#mermaid)
  - [github\action.py](#action)
  - [main.py](#main)
  - [main_v2.py](#main-v2)
  - [models\change_report.py](#change-report)
  - [models\config_models.py](#config-models)
  - [models\dependency_graph.py](#dependency-graph)
  - [models\generation_result.py](#generation-result)
  - [models\llm_models.py](#llm-models)
  - [models\metadata.py](#metadata)
  - [models\parsed_file.py](#parsed-file)
  - [models\scan_result.py](#scan-result)
  - [parsers\base_parser.py](#base-parser)
  - [parsers\javascript_parser.py](#javascript-parser)
  - [parsers\parser_factory.py](#parser-factory)
  - [parsers\python_parser.py](#python-parser)
  - [parsers\typescript_parser.py](#typescript-parser)
  - [test\test_change_detection.py](#test-change-detection)

---

## Architecture Overview

The project is structured into several modules, including analysis, generation, core, and parsers, with a main orchestrator that coordinates the workflow, and utilizes design patterns such as the factory pattern for creating parser and LLM provider instances

### Module Relationships

Modules connect through imports and function calls, with data flowing from the core scanner and parsers to the analysis modules, and then to the generation modules, which produce the final documentation output

## Design Patterns

- **Factory Pattern**
- **Observer Pattern**
- **Strategy Pattern**

---

## Module Reference

### analyzer

📄 `analysis\analyzer.py`

**Description:**

> Code analyzer using LLM for understanding and documentation.

**Purpose:**

Analyzes code modules using language models to generate documentation and project synthesis

**Responsibilities:**

- Analyzes individual code modules for structure and functionality
- Synthesizes cross-module relationships and project architecture

#### Classes

##### `class CodeAnalyzer`

Analyzes code using LLM to generate summaries and insights.

Supports both sync and async operation for flexibility.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `provider, api_key, temperature, max_tokens` | `None` | Initialize analyzer. |
| `from_config` | `llm_config` | `'CodeAnalyzer'` | Create analyzer from LLMConfig. |
| `analyze_module` | `parsed_file` | `ModuleSummary` | Analyze a single module synchronously. |
| `synthesize_project` | `module_summaries, project_path` | `ProjectAnalysis` | Synthesize project-level understanding synchronous... |
| `analyze_module_async` | `parsed_file` | `ModuleSummary` | Analyze a single module asynchronously. |
| `analyze_modules_async` | `parsed_files, max_concurrent` | `List[ModuleSummary]` | Analyze multiple modules concurrently. |

#### Dependencies

- `json`
- `asyncio`
- `typing`
- `models.parsed_file`
- `analysis.provider_factory`
- `analysis.llm_provider`
- `models.config_models`

---

### dependency_analyzer

📄 `analysis\dependency_analyzer.py`

**Description:**

> Builds a graph of how modules import each other. This help understand Project flow, Module importance, Circular dependencies, Analysis order

**Purpose:**

Analyzes Python project dependencies to build a graph showing module relationships, helping identify circular dependencies and module importance.

**Responsibilities:**

- Builds a dependency graph of module imports
- Detects circular dependencies and calculates module depths
- Generates summaries and Mermaid diagrams for visualization

#### Classes

##### `class DependencyAnalyzer`

Analyzes dependencies between project modules.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `project_root, parsed_files` | `None` | Initialize dependency analyzer. |
| `build_graph` | `` | `DependencyGraph` | Build the complete dependency graph. |
| `generate_summary` | `graph` | `str` | Generate text summary of dependency analysis. |
| `generate_mermaid` | `graph, max_nodes` | `str` | Generate Mermaid diagram syntax. |

#### Dependencies

- `pathlib`
- `typing`
- `collections`
- `models.parsed_file`
- `models.dependency_graph`
- `core.scanner`
- `parsers.python_parser`

---

### llm_provider

📄 `analysis\llm_provider.py`

**Description:**

> Abstract interface for LLM providers.

**Purpose:**

Provides an abstract interface for LLM providers with synchronous and asynchronous generation capabilities.

**Responsibilities:**

- Defines a standardized API for interacting with different LLM implementations
- Handles request retries and model configuration retrieval

#### Classes

##### `class BaseLLMProvider`

_Inherits from: `ABC`_

Abstract base class for LLM providers.

All LLM providers (Groq, OpenAI, Anthropic, etc.) must implement this interface.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `generate` | `prompt, model, system_prompt` | `LLMResponse` | Generate response from LLM (async). |
| `generate_sync` | `prompt, model, system_prompt` | `LLMResponse` | Generate response from LLM (synchronous). |
| `generate_with_retry` | `prompt, model, system_prompt, max_retries` | `LLMResponse` | Generate with automatic retry on failure. |
| `generate_sync_with_retry` | `prompt, model, system_prompt, max_retries` | `LLMResponse` | Sync version of generate_with_retry. |
| `get_model` | `size` | `str` | Get model name by size category. |

#### Dependencies

- `time`
- `asyncio`
- `abc`
- `models.llm_models`

---

### provider_factory

📄 `analysis\provider_factory.py`

**Description:**

> Factory for creating LLM providers.

**Purpose:**

Factory module for instantiating LLM providers based on configuration or direct parameters.

**Responsibilities:**

- Create and configure LLM provider instances (e.g., Groq, OpenAI)
- Initialize providers using either explicit parameters or configuration objects

#### Functions

##### `get_llm_provider`

```python
def get_llm_provider(provider: str, api_key: Optional[str], temperature: float, max_tokens: int, config: Optional[LLMConfig]) -> BaseLLMProvider
```

Factory function to create LLM provider.

Args:
    provider: Provider name
    api_key: API key
    temperature: Sampling temperature
    max_tokens: Max tokens
    config: Optional LLMConfig for model overrides

**Parameters:**

- `provider` (str) = `'groq'`
- `api_key` (Optional[str]) = `None`
- `temperature` (float) = `0.2`
- `max_tokens` (int) = `2500`
- `config` (Optional[LLMConfig]) = `None`

**Returns:** `BaseLLMProvider`

##### `get_llm_provider_from_config`

```python
def get_llm_provider_from_config(config: LLMConfig) -> BaseLLMProvider
```

Create provider directly from config.

This is the preferred way when you have a Config object.

**Parameters:**

- `config` (LLMConfig)

**Returns:** `BaseLLMProvider`

#### Dependencies

- `typing`
- `analysis.llm_provider`
- `analysis.providers.groq_provider`
- `analysis.providers.openai_provider`
- `models.config_models`

---

### __init__

📄 `analysis\providers\__init__.py`

**Description:**

> LLM provider implementations.

**Purpose:**

Serves as an entry point for LLM provider implementations, grouping related modules under the providers package.

**Responsibilities:**

- Initialize the providers package namespace
- Expose LLM provider implementations for external access

#### Dependencies

- `analysis.providers.groq_provider`
- `analysis.providers.openai_provider`

---

### groq_provider

📄 `analysis\providers\groq_provider.py`

**Description:**

> Groq LLM provider implementation.

**Purpose:**

Provides integration with Groq's LLM API for asynchronous and synchronous text generation

**Responsibilities:**

- Implement Groq-specific message formatting for API requests
- Handle both asynchronous and synchronous text generation workflows

#### Classes

##### `class GroqProvider`

_Inherits from: `BaseLLMProvider`_

Groq API provider implementation.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `api_key, temperature, max_tokens` | `None` | Initialize Groq provider. |
| `generate` | `prompt, model, system_prompt` | `LLMResponse` | Generate response asynchronously. |
| `generate_sync` | `prompt, model, system_prompt` | `LLMResponse` | Generate response synchronously. |

#### Dependencies

- `os`
- `typing`
- `groq`
- `analysis.llm_provider`
- `models.llm_models`

---

### openai_provider

📄 `analysis\providers\openai_provider.py`

**Description:**

> OpenAI LLM provider implementation.

**Purpose:**

Provides integration with OpenAI's language models for asynchronous and synchronous text generation.

**Responsibilities:**

- Initializing OpenAI API configuration
- Generating text responses using OpenAI's language models

#### Classes

##### `class OpenAIProvider`

_Inherits from: `BaseLLMProvider`_

OpenAI API provider implementation.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `api_key, temperature, max_tokens` | `None` | Initialize OpenAI provider. |
| `generate` | `prompt, model` | `LLMResponse` | Generate response asynchronously. |
| `generate_sync` | `prompt, model` | `LLMResponse` | Generate response synchronously. |

#### Dependencies

- `os`
- `typing`
- `openai`
- `analysis.llm_provider`
- `models.llm_models`

---

### quality_analyzer

📄 `analysis\quality_analyzer.py`

**Purpose:**

This module is intended for analyzing code quality metrics but currently contains no implemented functionality.

---

### commands

📄 `cli\commands.py`

**Purpose:**

This module is intended to handle command-line interface (CLI) commands but currently contains no implemented functions or classes.

**Responsibilities:**

- Parsing command-line arguments
- Dispatching CLI commands to appropriate handlers

---

### main

📄 `cli\main.py`

**Purpose:**

This module serves as the entry point for a command-line interface (CLI) application.

**Responsibilities:**

- Handling CLI command execution
- Providing the main runtime interface

---

### change_detector

📄 `core\change_detector.py`

**Purpose:**

Detects changes in files or data by comparing current state with cached metadata using hashing and metadata storage.

**Responsibilities:**

- Track file/data modifications through hash comparisons
- Manage metadata storage and retrieval for change detection

#### Classes

##### `class ChangeDetector`

Detects which files changed since last analysis.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `project_root` | `None` |  |
| `detect_changes` | `current_files` | `ChangeReport` | Compare current files against last analysis |
| `get_cached_summary` | `file_path` | `Optional[ModuleSummary]` | Get cached analysis for unchanged file. |
| `update_metadata` | `analyzed_files, summaries, project_name` | `None` | Update metadata after analysis. |
| `reload_metadata` | `` | `None` | Force re-read from disk (if external process modif... |

#### Dependencies

- `pathlib`
- `datetime`
- `typing`
- `core.hasher`
- `core.metadata_store`
- `models.metadata`
- `models.change_report`
- `models.parsed_file`
- `logging`

---

### config

📄 `core\config.py`

**Description:**

> Configuration management for Code Documentation Agent.

**Purpose:**

Manages configuration settings for the Code Documentation Agent, supporting JSON and YAML formats.

**Responsibilities:**

- Loading and saving configuration files in multiple formats (JSON/YAML)
- Providing default configuration templates and file discovery

#### Classes

##### `class ConfigManager`

Manages loading, saving, and accessing configuration.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `` | `None` |  |
| `load_from_file` | `config_path` | `Config` | Load configuration from file. |
| `save_to_file` | `config, output_path` | `None` | Save configuration to file. |
| `get_default_config` | `` | `Config` | Get default configuration. |
| `find_config_file` | `start_dir` | `Optional[Path]` | Search for config file in current directory and pa... |

#### Functions

##### `get_config_manager`

```python
def get_config_manager() -> ConfigManager
```

Get global config manager instance.

**Returns:** `ConfigManager`

##### `load_config`

```python
def load_config(config_path: Optional[Path], project_root: Optional[Path]) -> Config
```

Load configuration with smart defaults.

Args:
    config_path: Explicit path to config file
    project_root: Project root to search for config
    
Returns:
    Config instance

**Parameters:**

- `config_path` (Optional[Path]) = `None`
- `project_root` (Optional[Path]) = `None`

**Returns:** `Config`

#### Dependencies

- `os`
- `json`
- `pathlib`
- `typing`
- `models.config_models`
- `yaml`
- `yaml`

---

### hasher

📄 `core\hasher.py`

**Description:**

> This module provides utilities for hashing file contents to detect changes efficiently. It includes functions to generate hashes for individual files and batches of files, which can be used to compare against previous analyses and determine what has changed since the last run.

**Purpose:**

This module provides utilities for hashing file contents to detect changes efficiently.

**Responsibilities:**

- Generate hashes for individual files
- Generate hashes for batches of files to detect changes between runs

#### Classes

##### `class FileHasher`

Fast, reliable file hashing.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `hash_file` | `file_path` | `str` | Generate SHA-256 hash of file content. |
| `hash_files` | `file_paths` | `Dict[str, str]` | Hash multiple files efficiently. |

#### Dependencies

- `hashlib`
- `typing`
- `logging`

---

### metadata_store

📄 `core\metadata_store.py`

**Description:**

> This module manages the persistent storage of project metadata, including loading and saving metadata to disk. It provides a simple interface for the rest of the system to access and update metadata about files and projects, ensuring that change detection and analysis can be performed efficiently across runs.

**Purpose:**

Manages persistent storage and retrieval of project metadata, enabling efficient change detection and analysis across system runs.

**Responsibilities:**

- Loading and saving metadata to disk using JSON serialization
- Providing access to metadata state through methods like exists() and last_updated()

#### Classes

##### `class MetadataStore`

Persistent storage for project metadata.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `project_root` | `None` |  |
| `load` | `` | `Optional[ProjectMetadata]` | Load metadata from disk. |
| `save` | `metadata` | `None` | Save metadata to disk. |
| `clear` | `` | `None` | Delete metadata (force full reanalysis). |
| `exists` | `` | `bool` | Check if metadata file exists. |
| `last_updated` | `` | `Optional[datetime]` | Get last update time without loading full metadata... |

#### Dependencies

- `json`
- `pathlib`
- `typing`
- `datetime`
- `models.metadata`

---

### scanner

📄 `core\scanner.py`

**Description:**

> This module provides functionality to scan a project directory and return Python files with structural information.

**Purpose:**

Scans a project directory to identify Python files and extract their structural information.

**Responsibilities:**

- Traverse project directories while ignoring specified paths
- Collect Python files with their hierarchical structure and entry point metadata

#### Functions

##### `scan_project`

```python
def scan_project(project_path: str, ignore_dirs: List[str]) -> List[str]
```

Scan a project directory and return all Python files.

Args:
    project_path: Path to the project root.
    ignore_dirs: Directories to ignore during scanning.

Returns:
    List of relative path to .py files in the project.

**Parameters:**

- `project_path` (str)
- `ignore_dirs` (List[str]) = `None`

**Returns:** `List[str]`

##### `scan_project_with_tree`

```python
def scan_project_with_tree(project_path: str, ignore_dirs: List[str]) -> ScanResult
```

Scan project and return detailed structure with tree and metadata.

Args:
    project_path: Path to the project root
    ignore_dirs: Directories to ignore during scanning
    
Returns:
    ScanResult with tree structure, file list, and metadata

**Parameters:**

- `project_path` (str)
- `ignore_dirs` (List[str]) = `None`

**Returns:** `ScanResult`

##### `_check_entry_point`

```python
def _check_entry_point(file_path: Path) -> bool
```

Check if file has if __name__ == '__main__'.

**Parameters:**

- `file_path` (Path)

**Returns:** `bool`

#### Dependencies

- `pathlib`
- `typing`
- `models.scan_result`

---

### enhanced_generator

📄 `generation\enhanced_generator.py`

**Description:**

> Enhanced Documentation Generator

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

**Responsibilities:**

- Generate README.md, TECHNICAL_DOC.md, and API_REFERENCE.md documentation files
- Format module, class, and function details into structured documentation content

#### Classes

##### `class EnhancedDocumentationGenerator`

Generates comprehensive markdown documentation.

Unlike the basic generator, this one:
- Includes actual function signatures and parameters
- Documents all classes with their methods
- Generates API reference with full details
- Adds Table of Contents
- Includes dependency diagrams (if mermaid available)

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `output_dir` | `None` | Initialize the generator. |
| `generate_all` | `project_analysis, module_summaries, parsed_files, project_name, dependency_diagram, project_tree` | `GenerationResult` | Generate all documentation files. |

##### `class DocumentationGenerator`

_Inherits from: `EnhancedDocumentationGenerator`_

Alias for backward compatibility.

#### Dependencies

- `datetime`
- `pathlib`
- `typing`
- `models.generation_result`
- `models.parsed_file`
- `models.parsed_file`
- `time`

---

### generator

📄 `generation\generator.py`

**Description:**

> This module generates markdown documentation from analysis results.

**Purpose:**

This module generates markdown documentation from analysis results, focusing on creating README and technical documentation files.

**Responsibilities:**

- Generating README files with project structure and key information
- Generating detailed technical documentation for code analysis

#### Classes

##### `class DocumentationGenerator`

Generates README and technical documentation from analysis results.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `output_dir` | `None` | Initialize the documentation generator. |
| `generate_readme` | `project_analysis, project_name` | `str` | Generate README.md (overview documentation). |
| `generate_technical_doc` | `project_analysis, module_summaries, project_name` | `str` | Generate TECHNICAL_DOC.md (detailed technical docu... |
| `generate_all` | `project_analysis, module_summaries, project_name` | `Dict[str, str]` | Generate all documentation files (README and Techn... |

#### Dependencies

- `typing`
- `pathlib`
- `models.parsed_file`
- `models.parsed_file`

---

### graphviz

📄 `generation\visualizers\graphviz.py`

**Purpose:**

Provides integration with Graphviz for generating visual graphs and diagrams.

**Responsibilities:**

- Converting data structures into Graphviz DOT format
- Rendering visualizations using Graphviz tools

---

### mermaid

📄 `generation\visualizers\mermaid.py`

**Description:**

> Mermaid Diagram Generator

Generates Mermaid.js diagrams for:
- Module dependencies
- Class hierarchies
- Project architecture

**Purpose:**

Generates Mermaid.js diagrams for Python projects including class hierarchies, module dependencies, and architecture visualizations

**Responsibilities:**

- Creating class diagrams from parsed class data
- Generating dependency diagrams between modules/files
- Visualizing project architecture with Mermaid syntax

#### Classes

##### `class MermaidGenerator`

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

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `` | `None` |  |
| `class_diagram` | `classes, title` | `str` | Generate class relationship diagram. |
| `flowchart` | `steps, title` | `str` | Generate a flowchart. |
| `architecture_diagram` | `layers` | `str` | Generate architecture layer diagram. |
| `wrap_for_markdown` | `diagram` | `str` | Wrap diagram in markdown code fence. |

#### Functions

##### `generate_dependency_diagram`

```python
def generate_dependency_diagram(parsed_files: List) -> str
```

Quick function to generate dependency diagram.

**Parameters:**

- `parsed_files` (List)

**Returns:** `str`

##### `generate_class_diagram`

```python
def generate_class_diagram(classes: List) -> str
```

Quick function to generate class diagram.

**Parameters:**

- `classes` (List)

**Returns:** `str`

#### Dependencies

- `typing`
- `pathlib`
- `dataclasses`
- `models.parsed_file`

---

### action

📄 `github\action.py`

**Purpose:**

This module currently contains no functions, classes, or implementations and serves as an empty namespace or placeholder.

---

### main

📄 `main.py`

**Description:**

> Main orchestrator for the Code Documentation Agent.

**Purpose:**

Main orchestrator for generating code documentation by coordinating parsing, analysis, and generation components.

**Responsibilities:**

- Coordinates the documentation generation workflow for code projects
- Integrates parsing, analysis, and generation modules to produce cohesive documentation

#### Functions

##### `generate_documentation`

```python
def generate_documentation(project_path: str, project_name: str)
```

Complete pipeline: Scan → Parse → Analyze → Generate Docs

Args:
    project_path: Path to the project root
    project_name: Name of the project (uses folder name if not provided)

**Parameters:**

- `project_path` (str)
- `project_name` (str) = `None`

#### Dependencies

- `typing`
- `pathlib`
- `models.parsed_file`
- `parsers.python_parser`
- `core.scanner`
- `analysis.analyzer`
- `generation.generator`
- `traceback`

---

### main_v2

📄 `main_v2.py`

**Description:**

> Code Documentation Agent V2 - Main Orchestrator

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

**Responsibilities:**

- Coordinate multi-stage documentation pipeline (scan → analyze → generate)
- Manage configuration and output generation for code documentation

#### Functions

##### `generate_documentation`

```python
def generate_documentation(project_path: str, project_name: Optional[str], force: bool, provider: str, output_dir: Optional[str])
```

Complete documentation generation pipeline.

Args:
    project_path: Path to project root
    project_name: Name of project (defaults to folder name)
    force: If True, ignore cache and reanalyze everything
    provider: LLM provider ("groq" or "openai")
    output_dir: Output directory (defaults to output/{project_name})

**Parameters:**

- `project_path` (str)
- `project_name` (Optional[str]) = `None`
- `force` (bool) = `False`
- `provider` (str) = `'groq'`
- `output_dir` (Optional[str]) = `None`

#### Dependencies

- `time`
- `argparse`
- `typing`
- `pathlib`
- `models.parsed_file`
- `models.change_report`
- `parsers.python_parser`
- `core.scanner`
- `core.change_detector`
- `analysis.analyzer`
- _...and 5 more_

---

### change_report

📄 `models\change_report.py`

**Description:**

> This module defines the ChangeReport data model, which captures the differences between the current state of a project and its previous analysis. It identifies added, modified, deleted, and unchanged files to determine what needs to be re-analyzed.

**Purpose:**

Captures differences between project states to determine which files require re-analysis

**Responsibilities:**

- Tracks added/modified/deleted/unchanged files between analysis sessions
- Identifies files that need re-analysis based on detected changes

#### Classes

##### `class ChangeReport`

_Decorators: @dataclass_

Report of what changed since last analysis.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `has_changes` | `` | `bool` | Check if there are any changes. |
| `files_to_analyze` | `` | `List[str]` | List of files that need analysis (added or modifie... |
| `summary` | `` | `str` | Human-readable summary of changes |

#### Dependencies

- `dataclasses`
- `typing`

---

### config_models

📄 `models\config_models.py`

**Description:**

> Data models for configuration settings.

**Purpose:**

Defines data models for application configuration, including LLM, scanner, output, and change detection settings, and provides mechanisms to validate and instantiate components.

**Responsibilities:**

- Represent configuration parameters as dataclasses for type safety and clarity.
- Validate configuration values and provide defaults during initialization.
- Facilitate loading and accessing configuration data across the application.

#### Classes

##### `class LLMConfig`

_Decorators: @dataclass_

LLM provider configuration.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_model` | `size` | `str` | Get model name by size category. |

##### `class ScannerConfig`

_Decorators: @dataclass_

Scanner configuration.

##### `class OutputConfig`

_Decorators: @dataclass_

Output configuration.

##### `class ChangeDetectionConfig`

_Decorators: @dataclass_

Change detection configuration.

##### `class Config`

_Decorators: @dataclass_

Main configuration container.

#### Dependencies

- `os`
- `json`
- `pathlib`
- `typing`
- `dataclasses`

---

### dependency_graph

📄 `models\dependency_graph.py`

**Description:**

> Data models for module dependency analysis.

**Purpose:**

Models and analyzes dependencies between software modules, detecting relationships, coupling, and circular dependencies.

**Responsibilities:**

- Tracking module dependencies and their structural relationships
- Identifying circular dependencies and coupling metrics

#### Classes

##### `class ModuleNode`

_Decorators: @dataclass_

Represents a module in the dependency graph.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `is_leaf` | `` | `bool` | True if nothing imports this module. |
| `is_root` | `` | `bool` | True if this module doesn't import any internal mo... |
| `coupling_score` | `` | `int` | How coupled this module is (total connections). |

##### `class CircularDependency`

_Decorators: @dataclass_

Represents a circular dependency cycle.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `length` | `` | `int` | Number of modules in the cycle |

##### `class DependencyGraph`

_Decorators: @dataclass_

Graph of module dependencies.

This is a DATA model. All graph-building logic
lives in DependencyAnalyzer.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `total_modules` | `` | `int` | Total number of modules in the project. |
| `root_modules` | `` | `List[str]` | Modules that don't import any internal modules (ut... |
| `leaf_modules` | `` | `List[str]` | Modules that nothing else imports (dead code candi... |
| `most_imported` | `` | `List[tuple]` | Modules sorted by how many other modules import th... |
| `most_coupled` | `` | `List[tuple]` | Modules with highest coupling (most connections). |
| `has_circular_dependencies` | `` | `bool` | True if circular dependencies were detected. |
| `get_node` | `file_path` | `Optional[ModuleNode]` | Get a module node by file path. |
| `get_dependencies` | `file_path` | `List[str]` | Get all modules that the given file imports. |
| `get_dependents` | `file_path` | `List[str]` | Get all modules that import the given file. |
| `get_analysis_order` | `` | `List[str]` | Get optimal analysis order (topological sort). |
| `get_external_dependencies` | `` | `List[str]` | Get all unique external dependencies across the pr... |
| `get_modules_at_depth` | `depth` | `List[str]` | Get all modules at a specific depth from entry poi... |

#### Dependencies

- `pathlib`
- `dataclasses`
- `typing`

---

### generation_result

📄 `models\generation_result.py`

**Description:**

> Data model for generation results.

**Purpose:**

Defines a data model to represent the results of a generation process, including metadata and output details.

**Responsibilities:**

- Storing structured data about generated outputs
- Providing a summary representation of generation results

#### Classes

##### `class GenerationResult`

_Decorators: @dataclass_

Result of documentation generation.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `summary` | `` | `str` | Human-readable generation summary. |

#### Dependencies

- `datetime`
- `pathlib`
- `typing`
- `dataclasses`

---

### llm_models

📄 `models\llm_models.py`

**Description:**

> Data models for LLM interactions.

**Purpose:**

Defines data structures and custom exception classes for interacting with language model providers.

**Responsibilities:**

- Represent LLM responses in a structured dataclass.
- Provide specific exception types for provider errors, rate limits, authentication failures, and missing models.

#### Classes

##### `class LLMResponse`

_Decorators: @dataclass_

Standardized response from any LLM provider.

##### `class LLMProviderError`

_Inherits from: `Exception`_

Base error for LLM provider issues.

##### `class RateLimitError`

_Inherits from: `LLMProviderError`_

API rate limit hit.

##### `class AuthenticationError`

_Inherits from: `LLMProviderError`_

Invalid API key.

##### `class ModelNotFoundError`

_Inherits from: `LLMProviderError`_

Requested model doesn't exist.

#### Dependencies

- `dataclasses`

---

### metadata

📄 `models\metadata.py`

**Description:**

> This module defines data models for representing metadata about files and projects, including file hashes, last analysis timestamps, and summaries of file contents. This metadata is crucial for change detection and efficient re-analysis of only modified files.

**Purpose:**

This module defines data models for representing metadata about files and projects, including file hashes, last analysis timestamps, and summaries of file contents. This metadata is crucial for change detection and efficient re-analysis of only modified files.

**Responsibilities:**

- Track file and project metadata for change detection
- Store summaries and timestamps for efficient re-analysis

#### Classes

##### `class FileMetadata`

_Decorators: @dataclass_

Metadata about a single file.

##### `class ProjectMetadata`

_Decorators: @dataclass_

Metadata for entire project.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `to_json` | `` | `Dict` | Serialize to JSON for storage. |
| `from_json` | `data` | `'ProjectMetadata'` | Deserialize from JSON. |

#### Dependencies

- `dataclasses`
- `datetime`
- `typing`
- `models.parsed_file`

---

### parsed_file

📄 `models\parsed_file.py`

**Description:**

> This module defines data models for representing parsed information from Python files, including functions, classes, and modules. It also includes models for summarizing module and project-level insights after analysis.

**Purpose:**

Provides data models for representing parsed Python file elements and summarizing analysis at module and project levels.

**Responsibilities:**

- Represent functions, classes, imports, and parameters extracted from Python files
- Offer helper methods for introspection and string representation
- Enable conversion of module summaries to and from dictionaries
- Aggregate analysis results across modules for project-wide insights

#### Classes

##### `class ParameterInfo`

_Decorators: @dataclass_

Detailed parameter information.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|

##### `class FunctionInfo`

_Decorators: @dataclass_

Information about a function or method.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `signature` | `` | `str` | Generate readable signature. |

##### `class ClassInfo`

_Decorators: @dataclass_

Information about a class.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `is_dataclass` | `` | `bool` |  |

##### `class ImportInfo`

_Decorators: @dataclass_

Structured import information.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|

##### `class ParsedFile`

_Decorators: @dataclass_

Complete parsed information about a Python file.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `has_content` | `` | `bool` | Check if file has meaningful content to document. |
| `module_name` | `` | `str` | Extract module name from file path. |

##### `class ModuleSummary`

_Decorators: @dataclass_

Summary of a single module after LLM analysis.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `to_dict` | `` | `dict` | Convert to dict for JSON serialization |
| `from_dict` | `data` | `'ModuleSummary'` | Create ModuleSummary from dict |

##### `class ProjectAnalysis`

_Decorators: @dataclass_

High-level project understanding after synthesis.

#### Dependencies

- `dataclasses`
- `typing`
- `pathlib`

---

### scan_result

📄 `models\scan_result.py`

**Description:**

> Data models for project scanning results, including file trees, directory structures, and scan metadata.

**Purpose:**

This module defines data models for representing and processing project scanning results, including file/directory structures and metadata.

**Responsibilities:**

- Modeling file system structures as hierarchical data objects
- Providing methods to analyze and format scan output data

#### Classes

##### `class FileNode`

_Decorators: @dataclass_

Represents a file in the project.

##### `class DirectoryNode`

_Decorators: @dataclass_

Represents a directory in the project structure.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `to_tree_string` | `prefix, is_last` | `str` | Generate ASCII tree representation. |

##### `class ScanResult`

_Decorators: @dataclass_

Complete scan result with tree structure and metadata.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `total_size_mb` | `` | `float` | Total size in megabytes. |
| `get_tree_string` | `` | `str` | Get ASCII tree representation of project structure... |

#### Dependencies

- `dataclasses`
- `typing`

---

### base_parser

📄 `parsers\base_parser.py`

**Description:**

> Base parser interface for language-agnostic parsing.

**Purpose:**

Provides an abstract base class for language-agnostic file parsing interfaces.

**Responsibilities:**

- Defines common parsing interface for derived parser classes
- Specifies supported file extensions for language-specific parsers

#### Classes

##### `class BaseParser`

_Inherits from: `ABC`_

Abstract base class for all language parsers.

Each language (Python, JavaScript, etc.) implements this interface.
This allows the ParserFactory to work with any language uniformly.

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `project_root` | `None` |  |
| `parse_file` | `file_path` | `Optional[ParsedFile]` | Parse a single file and extract structured informa... |
| `parse_files` | `file_paths` | `List[ParsedFile]` | Parse multiple files. |
| `supported_extensions` | `` | `List[str]` | Return list of file extensions this parser handles... |

#### Dependencies

- `abc`
- `typing`
- `models.parsed_file`

---

### javascript_parser

📄 `parsers\javascript_parser.py`

**Purpose:**

This module is intended for parsing JavaScript code but currently contains no code, imports, classes, or functions.

**Responsibilities:**

- Parsing JavaScript code
- Handling JavaScript-specific syntax and structures

---

### parser_factory

📄 `parsers\parser_factory.py`

**Description:**

> Factory for creating appropriate parser based on file type.

**Purpose:**

Factory for creating appropriate parser based on file type.

**Responsibilities:**

- Instantiates the correct parser class based on file extension
- Maintains registry of supported parser types

#### Classes

##### `class ParserFactory`

Factory to get the right parser for each file type.

Usage:
    factory = ParserFactory(project_root="/path/to/project")
    parser = factory.get_parser("main.py")
    parsed = parser.parse_file("main.py")

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `project_root` | `None` |  |
| `get_parser` | `file_path` | `Optional[BaseParser]` | Get appropriate parser for a file. |
| `can_parse` | `file_path` | `bool` | Check if we have a parser for this file type. |
| `register_parser` | `extension, parser_class` | `None` | Register a new parser for an extension. |
| `supported_extensions` | `` | `list` | List all supported extensions. |

#### Dependencies

- `pathlib`
- `typing`
- `parsers.base_parser`
- `parsers.python_parser`

---

### python_parser

📄 `parsers\python_parser.py`

**Description:**

> This module provides functionality to parse Python files and extract structured information about classes, functions, imports, and docstrings.

**Purpose:**

This module parses Python files to extract structured information about classes, functions, imports, and docstrings.

**Responsibilities:**

- Parsing Python files to extract classes, functions, imports, and docstrings
- Providing methods to analyze and structure code elements like parameters, decorators, and global variables

#### Classes

##### `class PythonParser`

Enhanced Python parser using AST.

Extracts:
- Classes with base classes, decorators, methods
- Functions with parameters, types, decorators
- Structured imports
- Global variables
- Entry point detection

**Methods:**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | `project_root` | `None` |  |
| `parse_file` | `file_path` | `Optional[ParsedFile]` | Parse a Python file and extract all information. |
| `parse_files` | `file_paths` | `List[ParsedFile]` | Parse multiple files, skip failures. |

#### Functions

##### `parse_file`

```python
def parse_file(file_path: str, project_root: Optional[str]) -> Optional[ParsedFile]
```

Parse a single file (backward compatible).

**Parameters:**

- `file_path` (str)
- `project_root` (Optional[str]) = `None`

**Returns:** `Optional[ParsedFile]`

#### Dependencies

- `ast`
- `pathlib`
- `typing`
- `core.scanner`
- `models.parsed_file`
- `core.scanner`

---

### typescript_parser

📄 `parsers\typescript_parser.py`

**Purpose:**

This module is intended to parse TypeScript code, though it currently contains no implemented functionality.

**Responsibilities:**

- Parsing TypeScript syntax
- Converting TypeScript code to another format (unimplemented)

---

### test_change_detection

📄 `test\test_change_detection.py`

**Purpose:**

This module contains a test case for verifying the functionality of the change detection system in the core module.

**Responsibilities:**

- Testing the accuracy of change detection between file states
- Validating edge cases in change detection logic

#### Functions

##### `test_change_detection`

```python
def test_change_detection()
```

Test change detection on a real project.

#### Dependencies

- `sys`
- `pathlib`
- `core.change_detector`
- `models.parsed_file`

---


---

_Generated: 2026-04-12T14:19:00.769739_
_Modules documented: 36_