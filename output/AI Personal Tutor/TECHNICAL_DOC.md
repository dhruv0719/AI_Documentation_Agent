# AI Personal Tutor - Technical Documentation

## Architecture Overview

The project follows a modular design, with a FastAPI backend handling API requests, a Streamlit frontend for user interaction, and an AI core integrating language models and retrieval engines for generating responses. The architecture is structured around these components, facilitating a scalable and maintainable system.

## Module Relationships

Modules depend on each other through imports and function calls, with the AI core being central to the project's functionality, and the backend and frontend interacting through API endpoints. The data flow is orchestrated by the entry points, which initialize the necessary components and start the application.

## Design Patterns

- **Modular design**
- **Pipeline**
- **Factory**


---

## Module Reference


### `MVP\ai_core\engine\generate.py`

**Purpose:** This module orchestrates the AI generation process using a specified skill, leveraging LlamaIndex components and internal tools to produce responses.

**Responsibilities:**
- Initializes and configures the language model (LLM) for generation
- Sets up tools and agents with skill-specific prompts
- Coordinates data retrieval and response generation workflow
- Manages integration with the AI core's prompting and retrieval systems

**Key Components:**
- `run_generation_flow function`
- `LlamaIndex agent configuration`
- `Skill-specific prompt templates`
- `Data retrieval integration`

**Dependencies:**
- `json`
- `llama_index.core.llms`
- `llama_index.core.tools`
- `llama_index.core.agent`
- `llama_index.core.settings`
- `ai_core.prompts.templates`
- `ai_core.engine.retriever`

---

### `MVP\ai_core\engine\retriever.py`

**Purpose:** This module provides a retrieval engine for querying vector-stored data using ChromaDB and LlamaIndex.

**Responsibilities:**
- Initialize a ChromaDB vector store
- Configure a retrieval engine for semantic searches
- Provide an interface for querying stored embeddings

**Key Components:**
- `get_retrieval_engine()`
- `ChromaVectorStore`

**Dependencies:**
- `chromadb`
- `llama_index.core`
- `llama_index.vector_stores.chroma`

---

### `MVP\ai_core\llms.py`

**Purpose:** Configures global settings for LLMs and embeddings in the application

**Responsibilities:**
- Initializes Groq LLM integration
- Sets up HuggingFace embeddings
- Configures global LLM settings

**Key Components:**
- `setup_global_settings()`
- `Groq LLM integration`
- `HuggingFace embeddings`

**Dependencies:**
- `os`
- `dotenv`
- `llama_index.llms.groq`
- `llama_index.core.settings`
- `llama_index.embeddings.huggingface`

---

### `MVP\ai_core\prompts\templates.py`

**Purpose:** This module appears to be a placeholder or incomplete implementation related to prompt templates for an AI system, potentially integrating with the LlamaIndex framework.

**Responsibilities:**
- Serving as a namespace for prompt template definitions
- Providing integration points with LlamaIndex components
- Organizing template versions or configurations

**Key Components:**
- `llama_index.core imports (likely PromptTemplate or similar classes)`
- `Template configuration variables (not visible in metadata)`

**Dependencies:**
- `llama_index.core`

---

### `MVP\ai_core\script\ingest_data.py`

**Purpose:** Ingests web data into a ChromaDB vector store using LlamaIndex and HuggingFace embeddings for AI processing

**Responsibilities:**
- Load and process web data sources
- Generate text embeddings using HuggingFace models
- Store processed data in ChromaDB vector database
- Configure environment variables for API credentials

**Key Components:**
- `main() function for orchestration`
- `ChromaDB vector store integration`
- `LlamaIndex web readers for data extraction`
- `HuggingFace embeddings model`

**Dependencies:**
- `os`
- `chromadb`
- `llama_index.core`
- `llama_index.core`
- `llama_index.vector_stores.chroma`
- `llama_index.readers.web`
- `llama_index.embeddings.huggingface`
- `dotenv`

---

### `MVP\backend\api\__init__.py`

**Purpose:** Initializes the 'api' directory as a Python package and allows it to be imported as a module.

**Responsibilities:**
- Marks the directory as a Python package
- Enables module-level imports from the 'api' directory

**Key Components:**

---

### `MVP\backend\api\routes.py`

**Purpose:** This module defines FastAPI endpoints for a tutoring application, handling plan generation, user interaction, and progress tracking.

**Responsibilities:**
- Serves as the entry point for API requests related to tutoring plans
- Processes user questions and generates responses
- Tracks and updates learning progress
- Provides root endpoint for API health/status checks

**Key Components:**
- `generate_plan() function for creating study plans`
- `ask_user_question() for handling interactive queries`
- `track_progress() for updating learning status`
- `TutorServices integration for business logic`

**Dependencies:**
- `fastapi`
- `backend.model.schemas`
- `backend.services.tutor_services`

---

### `MVP\backend\app.py`

**Purpose:** Serves as the main entry point for the FastAPI application, initializing the API and integrating routes.

**Responsibilities:**
- Instantiates the FastAPI application
- Mounts API routes from backend.api.routes
- Configures middleware and application settings

**Key Components:**
- `FastAPI app instance`
- `Route imports from backend.api.routes`

**Dependencies:**
- `fastapi`
- `backend.api.routes`

---

### `MVP\backend\model\schemas.py`

**Purpose:** Defines data validation schemas for request payloads related to plan creation, question handling, and progress tracking using Pydantic models.

**Responsibilities:**
- Structuring expected input formats for API endpoints
- Validating incoming request data types and formats
- Providing type hints for request/response consistency

**Key Components:**
- `PlanRequest`
- `QuestionRequest`
- `ProgressUpdate`

**Dependencies:**
- `pydantic`

---

### `MVP\backend\services\tutor_services.py`

**Purpose:** This module provides functionalities to manage personalized learning plans, answer user questions, and track progress for a tutoring system.

**Responsibilities:**
- Generate customized learning plans based on user goals and skills
- Handle user inquiries related to learning topics
- Update and track user progress over time

**Key Components:**
- `generate_learning_plan`
- `ask_question`
- `update_progress`

---

### `MVP\backend\utils\memory.py`

**Purpose:** This module provides functions for loading and saving data to/from a JSON file, likely used for persistent storage or caching in the application.

**Responsibilities:**
- Serialize and save data to a JSON file
- Deserialize and load data from a JSON file
- Handle file path operations using the os module

**Key Components:**
- `save_data(data)`
- `load_data()`

**Dependencies:**
- `json`
- `os`

---

### `MVP\frontend\app.py`

**Purpose:** This module configures the AI core integration for a Streamlit-based frontend application, enabling interaction with language models.

**Responsibilities:**
- Initialize AI core configuration for the frontend
- Set up environment variables for AI services
- Integrate language model capabilities with Streamlit UI

**Key Components:**
- `configure_ai_core function`
- `ai_core.llms and ai_core.engine.generate modules`

**Dependencies:**
- `streamlit`
- `os`
- `sys`
- `json`
- `dotenv`
- `ai_core.llms`
- `ai_core.engine.generate`

---

### `Version_1\ai_core\engine\generate.py`

**Purpose:** This module handles the generation of AI responses using a specified skill, leveraging language models and retrieval components.

**Responsibilities:**
- Initialize and configure language models for response generation
- Integrate with retrieval systems to fetch context for generation
- Execute the generation workflow based on input skill parameters

**Key Components:**
- `run_generation_flow function`
- `llama_index.core.llms integration`

**Dependencies:**
- `json`
- `llama_index.core.llms`
- `llama_index.core.tools`
- `llama_index.core.agent`
- `llama_index.core.settings`
- `ai_core.prompts.templates`
- `ai_core.engine.retriever`

---

### `Version_1\ai_core\engine\retriever.py`

**Purpose:** This module creates and configures a retrieval engine using ChromaDB and LlamaIndex for querying vectorized data.

**Responsibilities:**
- Initializes a Chroma vector store for data retrieval
- Configures a LlamaIndex retrieval engine with specified parameters
- Integrates vector store with AI-powered query processing

**Key Components:**
- `get_retrieval_engine`
- `ChromaVectorStore`
- `RetrievalEngine`

**Dependencies:**
- `chromadb`
- `llama_index.core`
- `llama_index.vector_stores.chroma`

---

### `Version_1\ai_core\llms.py`

**Purpose:** Configures global settings for AI language models and embeddings in the application

**Responsibilities:**
- Initializes global LLM (Groq) and embedding (HuggingFace) configurations
- Sets environment variables for API credentials
- Centralizes AI model configuration for consistent application-wide use

**Key Components:**
- `setup_global_settings() function`
- `Groq LLM integration`
- `HuggingFace embeddings setup`

**Dependencies:**
- `os`
- `dotenv`
- `llama_index.llms.groq`
- `llama_index.core.settings`
- `llama_index.embeddings.huggingface`

---

### `Version_1\ai_core\prompts\templates.py`

**Purpose:** This module appears to be an empty or incomplete implementation intended for prompt template definitions, but contains no actual code or functionality.

**Responsibilities:**
- Serving as a placeholder for prompt template configurations
- Potentially providing structured prompt templates for AI interactions
- Integrating with llama_index.core components for prompt management

**Key Components:**
- `llama_index.core import (unutilized)`
- `Unnamed template structure (not implemented)`

**Dependencies:**
- `llama_index.core`

---

### `Version_1\ai_core\script\ingest_data.py`

**Purpose:** Ingests and processes data for an AI system using ChromaDB and LlamaIndex components

**Responsibilities:**
- Load and process web-based source documents
- Generate embeddings using HuggingFace models
- Store processed data in Chroma vector database

**Key Components:**
- `main() function for execution flow`
- `ChromaVectorStore integration`

**Dependencies:**
- `os`
- `chromadb`
- `llama_index.core`
- `llama_index.core`
- `llama_index.vector_stores.chroma`
- `llama_index.readers.web`
- `llama_index.embeddings.huggingface`
- `dotenv`

---

### `Version_1\backend\api\__init__.py`

**Purpose:** Serves as an initializer for the 'api' package, enabling it to be recognized as a Python package.

**Responsibilities:**
- Initializing the package structure
- Providing a namespace for API-related modules

**Key Components:**

---

### `Version_1\backend\api\routes.py`

**Purpose:** This module provides database dependency management for FastAPI routes and integrates with Celery task results.

**Responsibilities:**
- Manages database session lifecycle for API endpoints
- Provides dependency injection for route handlers
- Facilitates Celery task result retrieval

**Key Components:**
- `get_db() database dependency`
- `SQLAlchemy ORM session management`

**Dependencies:**
- `fastapi`
- `celery.result`
- `backend.model.schemas`
- `backend.tasks`
- `backend.database`
- `backend.model.db_models`
- `sqlalchemy.orm`

---

### `Version_1\backend\database.py`

**Purpose:** Configures and initializes the database connection using SQLAlchemy for the application.

**Responsibilities:**
- Establishes a connection to the database using environment variables
- Sets up SQLAlchemy's declarative base for model definitions
- Provides session management for database interactions

**Key Components:**
- `SQLAlchemy engine creation`
- `Declarative base class configuration`

**Dependencies:**
- `os`
- `sqlalchemy`
- `sqlalchemy.orm`
- `sqlalchemy.ext.declarative`
- `dotenv`

---

### `Version_1\backend\main.py`

**Purpose:** Serves as the entry point for the FastAPI backend application, initializing the application and providing a health check endpoint.

**Responsibilities:**
- Initializes the FastAPI application
- Includes API routes from backend.api.routes
- Loads environment variables using dotenv
- Provides a health check endpoint to verify service availability

**Key Components:**
- `health_check() function`
- `FastAPI application instance (implied by fastapi import)`

**Dependencies:**
- `fastapi`
- `backend.api.routes`
- `dotenv`

---

### `Version_1\backend\model\db_models.py`

**Purpose:** Defines SQLAlchemy data models for learning plans and their modules in the application's database

**Responsibilities:**
- Establishing database schema structure for educational content
- Mapping Python classes to SQL database tables
- Defining relationships between learning plans and modules

**Key Components:**
- `LearningPlan (primary data model for educational plans)`
- `PlanModule (related data model representing content modules)`

**Dependencies:**
- `sqlalchemy`
- `sqlalchemy.orm`
- `sqlalchemy.sql`
- `backend.database`

---

### `Version_1\backend\model\schemas.py`

**Purpose:** Defines data validation schemas for learning plan management using Pydantic models

**Responsibilities:**
- Structuring request/response data for plan creation and status checks
- Ensuring data consistency across API endpoints
- Providing type hints for learning plan modules

**Key Components:**
- `PlanRequest (input validation model)`
- `LearningPlanSchema (core plan structure definition)`

**Dependencies:**
- `pydantic`
- `typing`

---

### `Version_1\backend\services\tutor_services.py`

**Purpose:** This module provides core functionalities for managing user learning plans, handling questions, and tracking progress in a tutoring system.

**Responsibilities:**
- Generating customized learning plans based on user goals and skills
- Handling user-submitted questions and providing responses
- Tracking and updating user progress over time

**Key Components:**
- `generate_learning_plan(username: str, skill: str, period_in_week: int, goal: str)`
- `ask_question(username: str, question: str)`
- `update_progress(username: str, day: int, status: str)`

---

### `Version_1\backend\tasks.py`

**Purpose:** Handles asynchronous generation of plans using AI models and database integration

**Responsibilities:**
- Executes Celery tasks for plan generation
- Interfaces with AI model engine for content generation
- Coordinates database operations for task persistence

**Key Components:**
- `async_generate_plan Celery task`
- `ai_core.engine.generate integration`

**Dependencies:**
- `celery`
- `os`
- `sys`
- `ai_core.engine.generate`
- `ai_core.llms`
- `backend.database`
- `backend.model.db_models`

---

### `Version_1\backend\utils\memory.py`

**Purpose:** Handles loading and saving data to a file using JSON serialization for persistent storage.

**Responsibilities:**
- Load data from a JSON file
- Save data to a JSON file
- Manage file path operations using os module

**Key Components:**
- `load_data()`
- `save_data(data)`

**Dependencies:**
- `json`
- `os`

---

### `Version_1\frontend\app.py`

**Purpose:** Fetches plan details from an API and supports frontend display using Streamlit

**Responsibilities:**
- Retrieve plan information by ID via HTTP requests
- Integrate API data with Streamlit frontend interface
- Handle request timing and potential retries

**Key Components:**
- `get_plan function for API interaction`
- `Streamlit framework integration`

**Dependencies:**
- `streamlit`
- `requests`
- `time`

---

### `Version_1\scripts\create_tables.py`

**Purpose:** This module initializes and creates database tables based on the defined models.

**Responsibilities:**
- Establishes database connections using environment configurations
- Executes table creation commands for all defined models
- Handles potential errors during database initialization

**Key Components:**
- `backend.database.connection`
- `backend.model.metadata.create_all`

**Dependencies:**
- `os`
- `sys`
- `backend.database`
- `backend.model`

---

### `ai_core\agents\tutor_agent.py`

**Purpose:** This module provides AI-driven educational assistance by generating personalized learning plans and answering user questions.

**Responsibilities:**
- Generate structured learning plans based on user-specified skills, goals, and timeframes
- Provide accurate answers to user questions using AI capabilities
- Leverage a language model wrapper for intelligent response generation

**Key Components:**
- `generate_learning_plan_ai() function`
- `answer_user_question_ai() function`
- `LLM_wrapper import for AI model integration`

**Dependencies:**
- `ai_core.models.LLM_wrapper`

---

### `ai_core\engine\generate.py`

**Purpose:** This module handles the generation of AI responses using a specified skill, likely integrating a language model with retrieval mechanisms.

**Responsibilities:**
- Initialize and configure the language model (LLM) for generation
- Execute a generation flow combining retrieval and LLM processing
- Manage skill-specific prompt templates and agent workflows

**Key Components:**
- `run_generation_flow function`
- `LLM instance from llama_index.core.llms`

**Dependencies:**
- `json`
- `llama_index.core.llms`
- `llama_index.core.tools`
- `llama_index.core.agent`
- `llama_index.core.settings`
- `ai_core.prompts.templates`
- `ai_core.engine.retriever`

---

### `ai_core\engine\retriever.py`

**Purpose:** This module sets up a retrieval engine using ChromaDB and LlamaIndex for querying vectorized data stores.

**Responsibilities:**
- Initializing a ChromaDB vector store
- Configuring a LlamaIndex retrieval engine
- Enabling semantic search over stored embeddings

**Key Components:**
- `get_retrieval_engine()`
- `ChromaVectorStore`

**Dependencies:**
- `chromadb`
- `llama_index.core`
- `llama_index.vector_stores.chroma`

---

### `ai_core\llms.py`

**Purpose:** Configures global settings for language models and embeddings in an AI core system.

**Responsibilities:**
- Initializes environment variables using dotenv
- Sets up Groq LLM integration via llama_index
- Configures HuggingFace embeddings

**Key Components:**
- `setup_global_settings function`
- `llama_index.llms.groq integration`
- `llama_index.embeddings.huggingface setup`

**Dependencies:**
- `os`
- `dotenv`
- `llama_index.llms.groq`
- `llama_index.core.settings`
- `llama_index.embeddings.huggingface`

---

### `ai_core\models\LLM_wrapper.py`

**Purpose:** This module provides a wrapper for interacting with the Groq API to perform chat-based language model operations.

**Responsibilities:**
- Initializing and configuring the Groq API client
- Sending chat messages to a specified language model
- Handling API response parsing and error handling

**Key Components:**
- `groq_chat function for API interaction`
- `Groq client instance from the groq library`

**Dependencies:**
- `os`
- `dotenv`
- `groq`

---

### `ai_core\prompts\templates.py`

**Purpose:** Provides prompt template configurations for AI core operations using llama_index integration

**Responsibilities:**
- Defines standardized prompt structures for AI interactions
- Serves as template base for derivative prompt modules
- Facilitates llama_index prompt system integration

**Key Components:**
- `llama_index.core integration hooks`
- `Template configuration placeholders`

**Dependencies:**
- `llama_index.core`

---

### `ai_core\script\ingest_data.py`

**Purpose:** Ingests data into a vector store using ChromaDB and LlamaIndex for AI processing

**Responsibilities:**
- Load environment variables for configuration
- Initialize ChromaDB vector store connection
- Fetch and process web data using LlamaIndex readers
- Ingest processed data into vector store

**Key Components:**
- `main() function`
- `llama_index.vector_stores.chroma.ChromaVectorStore`

**Dependencies:**
- `os`
- `chromadb`
- `llama_index.core`
- `llama_index.vector_stores.chroma`
- `llama_index.readers.web`
- `dotenv`

---

### `backend\api\__init__.py`

**Purpose:** Serves as an initializer for the 'api' package, enabling Python to recognize the directory as a package.

**Responsibilities:**
- Marking the directory as a Python package
- Providing a namespace for API-related modules

**Key Components:**

---

### `backend\api\routes.py`

**Purpose:** This module defines FastAPI routes for a tutoring application, handling plan generation, user interaction, and progress tracking.

**Responsibilities:**
- Exposes API endpoints for plan generation and question handling
- Validates and processes incoming request data using Pydantic schemas
- Coordinates with tutor services to execute business logic

**Key Components:**
- `generate_plan() endpoint for creating study plans`
- `ask_user_question() for handling tutoring interactions`

**Dependencies:**
- `fastapi`
- `backend.model.schemas`
- `backend.services.tutor_services`

---

### `backend\app.py`

**Purpose:** Serves as the main entry point for the FastAPI application, integrating API routes.

**Responsibilities:**
- Initializes the FastAPI application instance
- Mounts and registers API routes from backend.api.routes
- Provides the application object for deployment

**Key Components:**
- `FastAPI application instance`
- `Route registration from backend.api.routes`

**Dependencies:**
- `fastapi`
- `backend.api.routes`

---

### `backend\config.py`

**Purpose:** This module is intended to hold configuration settings for the backend application, though it currently contains no implemented code.

**Responsibilities:**
- Storing application configuration parameters
- Providing default values for system settings
- Managing environment-specific variables

**Key Components:**

---

### `backend\model\schemas.py`

**Purpose:** Defines data validation schemas for request payloads and internal data structures using Pydantic

**Responsibilities:**
- Validating and serializing request data
- Enforcing consistent data structures across the application
- Serving as contract interfaces between API layers and business logic

**Key Components:**
- `PlanRequest`
- `QuestionRequest`
- `ProgressUpdate`

**Dependencies:**
- `pydantic`

---

### `backend\services\tutor_services.py`

**Purpose:** Provides tutoring-related services for users including generating learning plans, answering questions, and tracking progress.

**Responsibilities:**
- Generates customized learning plans based on user goals and skills
- Handles user questions and provides tutoring responses
- Tracks and updates user progress over time

**Key Components:**
- `generate_learning_plan(username: str, skill: str, period_in_week: int, goal: str)`
- `ask_question(username: str, question: str)`
- `update_progress(username: str, day: int, status: str)`

---

### `backend\utils\memory.py`

**Purpose:** This module provides functions for loading and saving data using JSON, likely for persistent storage in a file-based system.

**Responsibilities:**
- Load data from a JSON file
- Save data to a JSON file
- Manage file paths using os module

**Key Components:**
- `load_data()`
- `save_data()`

**Dependencies:**
- `json`
- `os`

---

### `frontend\app.py`

**Purpose:** This module serves as the frontend entry point for configuring and initializing AI core components within a Streamlit web application.

**Responsibilities:**
- Setting up environment variables using dotenv
- Configuring AI core language models (LLMs) and generation engines
- Establishing integration between Streamlit frontend and AI backend

**Key Components:**
- `configure_ai_core() function`
- `ai_core.engine.generate module`

**Dependencies:**
- `streamlit`
- `os`
- `sys`
- `json`
- `dotenv`
- `ai_core.llms`
- `ai_core.engine.generate`

---

### `run_ai_core_test.py`

**Purpose:** This module tests the AI core functionality by initializing language models and generation engine.

**Responsibilities:**
- Loads environment variables using dotenv
- Initializes AI core components (LLMs and generation engine)
- Executes test workflows for AI core validation

**Key Components:**
- `main() function`
- `ai_core.llms`
- `ai_core.engine.generate`

**Dependencies:**
- `json`
- `dotenv`
- `ai_core.llms`
- `ai_core.engine.generate`

---


## Development Guidelines

[Add coding standards, contribution guidelines, etc.]

## Testing

[Add testing instructions]

---

*This technical documentation was automatically generated by the Code Documentation Agent.*
