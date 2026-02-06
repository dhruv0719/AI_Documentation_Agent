# Technical Design – Code Documentation Agent (V1)

## Objective
The goal of this system is to automatically analyze a codebase and generate
up-to-date documentation that helps both general users and developers
understand the project without manually reading the code.

The system focuses on **Python-based repositories in V1** and supports
local folders or GitHub repositories.

---

## Supported Inputs (V1)
- Local Python project directory
- Public GitHub repository (manual clone)

---

## Supported Outputs (V1)
- README.md (High-level overview documentation)
- TECHNICAL_DOC.md (Developer-focused technical documentation)

---

## Tech Stack

### Programming Language
- **Python 3.10+**
  - Strong ecosystem for AST parsing
  - Best support for LLM tooling
  - Fast prototyping and maintainability

### Code Analysis
- `os`, `pathlib` – file traversal
- `ast` – Python Abstract Syntax Tree parsing
- (Future) Tree-sitter for multi-language support

### LLM Integration
- LLM Provider: OpenAI / Groq / Local LLM (configurable)
- Prompting Strategy:
  - Structured prompts
  - File-level summaries
  - Function- and class-level reasoning

### Change Tracking (Deferred in V1)
- File content hashing (SHA256)
- Stored metadata in JSON

### Output Format
- Markdown (`.md`)
- Human-readable and version-controllable

---

## System Components

### 1. Repository Scanner
**Responsibility**
- Traverse project directory
- Ignore non-relevant files (venv, node_modules, .git)
- Build a structured file tree

**Output**
- List of source files
- Folder hierarchy representation

---

### 2. Code Parser
**Responsibility**
- Parse Python files using AST
- Extract:
  - Classes
  - Functions
  - Method signatures
  - Docstrings (if present)

**Output**
- Structured JSON representation of code elements

---

### 3. Code Understanding Module
**Responsibility**
- Convert parsed code into semantic meaning
- Identify:
  - Purpose of modules
  - Responsibilities of classes/functions
  - API boundaries

**Implementation**
- AST data + LLM reasoning
- No raw file dumping into LLM

---

### 4. Documentation Generator
**Responsibility**
Generate two documentation types:

#### Overview Documentation (README.md)
- Project purpose
- High-level architecture
- Setup instructions
- Folder structure explanation

#### Technical Documentation (TECHNICAL_DOC.md)
- Module responsibilities
- Function and class explanations
- Architecture decisions
- Developer notes

---

## Design Principles
- **Deterministic first, AI second**
- **Readable output over fancy language**
- **Modular architecture**
- **LLM as an assistant, not a source of truth**

---

## Limitations (V1)
- Python-only support
- Manual execution (CLI)
- No real-time GitHub webhook integration
- No partial doc updates (full regeneration only)

---

## Future Enhancements
- Git-based change detection
- Incremental documentation updates
- Multi-language support
- Multi-agent execution
- Web dashboard
