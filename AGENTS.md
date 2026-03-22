# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Build/Lint/Test Commands

- Run tests: `pytest`
- Run a single test file: `pytest tests/test_knowledge_base.py`
- Run a specific test: `pytest tests/test_knowledge_base.py::test_knowledge_base_query`
- Run the application: `uv run apply` or `uv run python main.py`

## Non-Obvious Project Patterns

### Configuration & Setup

- Project uses `browser-use` library (not Playwright/Selenium) for browser automation with custom Agent architecture
- Configuration is loaded from [`app/config.py`](app/config.py) with environment variable fallbacks using `python-dotenv`
- Browser executable path defaults to Edge on Windows: `"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"`
- Profile directory is set to `./profile` in project root with `Default` profile name
- NVIDIA API is used for browser agents with `BROWSER_AGENT_NVIDIA_MODEL` and `NVIDIA_BASE_URL` configuration
- Groq API is used for resume ranking with `RESUME_AGENT_GROQ_MODEL` configuration

### Agent Architecture

- [`app/session_pool.py`](app/session_pool.py) manages browser instances with multi-tenant support via `SessionPool` class
- Four main agents are defined in [`app/agents/`](app/agents/) directory:
  - [`JobSearchAgent`](app/agents/job_search_agent.py): Searches and filters jobs using NVIDIA LLM
  - [`JobApplicationAgent`](app/agents/job_application_agent.py): Applies to jobs using NVIDIA LLM with knowledge base tools
  - [`KnowledgeBaseAgent`](app/agents/knowledge_base_agent.py): Manages applicant data using mem0 with Qdrant
  - [`ResumeManagerAgent`](app/agents/resume_manager_agent.py): Handles resume selection using Groq LLM
- All agents use `get_logger()` from [`app/logger_config.py`](app/logger_config.py) for logging

### Knowledge Base System

- Uses `mem0` memory framework with Qdrant vector store for knowledge base functionality
- Knowledge base files must be in [`user_data/knowledge_base/`](user_data/knowledge_base/) directory (`.txt` or `.md` files only)
- Memory configuration requires specific providers: `groq` for LLM, `langchain` for embeddings with Cohere model, `cohere` for reranking
- Knowledge base queries must use `user_id="applicant"` metadata for proper context
- The [`KnowledgeBaseAgent`](app/agents/knowledge_base_agent.py) exposes a `query()` method that returns formatted facts

### Resume Management

- Resume PDFs must be stored in [`user_data/resumes/`](user_data/resumes/) directory
- Resume selection uses Groq LLM ranking with specific prompt template requiring "Resume ID" numbering format
- When only one resume exists, it's automatically selected without LLM ranking
- The [`ResumeManagerAgent`](app/agents/resume_manager_agent.py) uses `pypdf` for PDF text extraction

### Browser Agent Configuration

- Browser agents use NVIDIA API with `ChatOpenAI` from `browser_use.llm`
- Model: `BROWSER_AGENT_NVIDIA_MODEL` (default: `qwen/qwen3.5-397b-a17b`)
- Base URL: `NVIDIA_BASE_URL` (default: `https://integrate.api.nvidia.com/v1/`)
- The `reasoning_effort` parameter is set to `"low"` for browser agents
- Agents are initialized with `browser` session from `SessionPool`

### Testing Conventions

- Test files must include the project root path insertion: `sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))`
- Tests may be skipped if API keys are missing (common pattern for LLM-dependent tests)
- Test files must be in [`tests/`](tests/) directory
- Use `pytest.mark.asyncio` decorator for async tests
- Mock LLM responses using `AsyncMock` for `ainvoke` method

### Logging

- Always use the custom `get_logger()` function from [`app/logger_config.py`](app/logger_config.py) for consistent logging format
- Uses `colorlog` for colored console output with specific format: `'%(asctime)s - %(name)s - %(log_color)s%(levelname)s%(reset)s - %(message)s'`
- Logger names follow module hierarchy with `job_agent` as root logger (e.g., `get_logger(__name__)`)
- Call `setup_logger()` in `main.py` to configure the root logger before creating agent loggers

### Error Handling

- Job fit analysis defaults to `is_fit=True` when errors occur to avoid blocking applications
- Resume ranking falls back to first resume when parsing errors occur
- Knowledge base returns "No relevant information found in the knowledge base." message rather than empty results
- All agent methods use try/except blocks with appropriate logging

### LLM Response Models

- Custom Pydantic models are defined in [`app/models/llm_responses.py`](app/models/llm_responses.py)
- Use `JobFitAnalysis` model for job fit analysis with `is_fit` (bool) and `reasoning` (str) fields
- LLM responses are parsed using `output_format` parameter in `ainvoke` calls

### Key Dependencies

- `browser-use>=0.12.0`: Browser automation framework
- `mem0ai>=1.0.4`: Memory/knowledge base framework
- `langchain>=1.2.10`, `langchain-cohere>=0.5.0`, `langchain-core>=1.2.16`: LLM integration
- `pypdf>=6.6.0`: PDF text extraction
- `colorlog>=6.10.1`: Colored logging
- `pytest>=9.0.2`: Testing framework
