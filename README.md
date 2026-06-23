# 🤖 AI Documentation Agent (DocAgent)

An AI-powered documentation system that automatically analyzes Python codebases and generates structured developer documentation using Abstract Syntax Tree (AST) analysis and Large Language Models (LLMs).

---

## 📖 Overview

Maintaining software documentation is one of the most neglected and time-consuming tasks in software development. As projects evolve, documentation quickly becomes outdated, making onboarding, maintenance, and knowledge transfer difficult.

DocAgent solves this problem by automatically understanding a Python codebase, extracting its structure and dependencies, and generating professional developer documentation directly from source code.

The system combines static code analysis with Large Language Models to transform raw code into human-readable technical documentation.

---

## ✨ Key Features

* 🌳 AST-based source code analysis
* 🔍 Automatic extraction of:

  * Functions
  * Classes
  * Methods
  * Imports
  * Dependencies
* 🤖 AI-generated project documentation
* 🔄 Incremental documentation updates through change detection
* 🕸️ Dependency graph analysis
* 📊 Mermaid diagram generation
* 🏗️ Architecture summarization
* ⚡ Multi-provider LLM support

  * Groq
  * OpenAI
* 🧩 Modular and extensible design

---

## 🎯 Problem Statement

Software teams often spend significant time writing and maintaining documentation.

Common challenges include:

* 📅 Outdated documentation
* 🚀 Poor onboarding experience
* 👀 Lack of architectural visibility
* 🏝️ Knowledge silos inside teams
* ⏳ High maintenance overhead

DocAgent automates documentation generation by directly analyzing source code and continuously producing up-to-date developer documentation.

---

## 🏗️ System Architecture

![System Architecture](assets/system-architecture.png)

```text
Python Codebase
       │
       ▼
 Project Scanner
       │
       ▼
 AST Parser
       │
       ▼
 Dependency Analyzer
       │
       ▼
 Change Detection Engine
       │
       ▼
 LLM Documentation Generator
       │
       ▼
 Markdown Documentation
```

---

## ⚙️ How It Works

### 📂 Step 1 — Project Scanning

The system scans the target Python project and discovers all source files.

### 🌳 Step 2 — AST Analysis

Python's Abstract Syntax Tree (AST) is used to extract:

* Classes
* Methods
* Functions
* Imports
* Dependencies

### 🔗 Step 3 — Dependency Analysis

The project structure is analyzed to understand module relationships and architecture.

### 🔄 Step 4 — Change Detection

The system identifies modifications between documentation generations to avoid unnecessary processing.

### 🤖 Step 5 — Documentation Generation

Structured metadata is passed to an LLM which generates:

* Project Overview
* Architecture Summary
* Module Documentation
* Dependency Reports
* Setup Instructions
* Technical Explanations

### 📊 Step 6 — Visualization

Mermaid diagrams are generated automatically to visualize dependency relationships.

---

## 📝 Example

### 💻 Input Code

```python
class User:
    def login(self):
        pass

    def logout(self):
        pass
```

### 📄 Generated Documentation

```markdown
### User

Represents an application user.

Methods:
- login(): Authenticates the user.
- logout(): Terminates the active session.
```

---

## 📦 Generated Outputs

The generated documentation may include:

* 📖 Project Overview
* 🏗️ Architecture Summary
* 📚 Module Documentation
* 🔍 Dependency Analysis
* 🎨 Design Patterns
* 🚪 Entry Points
* ⚙️ Setup Guide
* 📊 Mermaid Dependency Diagrams
* 🤖 AI-Generated Technical Explanations

---

## 🛠️ Tech Stack

| Category                | Technologies                               |
| ----------------------- | ------------------------------------------ |
| 💻 Programming Language | Python                                     |
| 🌳 Code Analysis        | AST                                        |
| 🤖 AI Models            | Groq API, OpenAI API                       |
| 📄 Documentation        | Markdown                                   |
| 📊 Visualization        | Mermaid                                    |
| 🏗️ Design Principles   | OOP, Factory Pattern, Modular Architecture |


## ⚡ Installation

### 📥 Clone Repository

```bash
git clone https://github.com/dhruv0719/AI_Documentation_Agent.git

cd AI_Documentation_Agent
```

### 🐍 Create Virtual Environment

```bash
python -m venv .venv
```

### ▶️ Activate Environment

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

### 🔑 Configure Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
```

---

## 🎮 Usage

Run the application:

```bash
python main_v2.py
```

The system will:

1. 📂 Scan the project
2. 🌳 Parse source files
3. 🔗 Analyze dependencies
4. 🔄 Detect changes
5. 🤖 Generate documentation
6. 📄 Export markdown reports


---

## 🔮 Future Improvements

* 🌍 Multi-language support

  * JavaScript
  * Java
  * C++
* 🔗 GitHub Repository Integration
* 📄 Automatic README Generation
* 🌐 Interactive Documentation Website
* 🔍 Semantic Code Search
* 🏗️ Architecture Diagram Generation
* ⚙️ GitHub Actions Integration
* 📊 Documentation Quality Evaluation Pipeline

---
