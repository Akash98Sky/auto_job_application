# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Build/Lint/Test Commands

- Run tests: `pytest`
- Run a single test file: `pytest tests/test_knowledge_base.py`
- Run a specific test: `pytest tests/test_knowledge_base.py::test_knowledge_base_query`

## Non-Obvious Project Patterns

### Configuration & Setup
- Project uses `browser-use` library (not Playwright/Selenium) for browser automation with custom Agent architecture
- Configuration is loaded from [`app/config.py`](app/config.py) with environment variable fallbacks using `python-dotenv`
- Browser executable path defaults to Edge on Windows: `"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"`
- Profile directory is set to `./profile` in project root with `Default` profile name

### Knowledge Base System
- Uses `mem0` memory framework with Qdrant vector store for knowledge base functionality
- Knowledge base files must be in [`user_data/knowledge_base/`](user_data/knowledge_base/) directory (`.txt` or `.md` files only)
- Memory configuration requires specific providers: `groq` for LLM, `langchain` for embeddings with Cohere model, `cohere` for reranking
- Knowledge base queries must use `user_id="applicant"` metadata for proper context

### Resume Management
- Resume PDFs must be stored in [`user_data/resumes/`](user_data/resumes/) directory
- Resume selection uses LLM ranking with specific prompt template requiring "Resume ID" numbering format
- When only one resume exists, it's automatically selected without LLM ranking

### Testing Conventions
- Test files must include the project root path insertion: `sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))`
- Tests may be skipped if API keys are missing (common pattern for LLM-dependent tests)
- Test files must be in same directory structure as source files (not separate test folder)

### Logging
- Always use the custom `get_logger()` function from [`app/logger_config.py`](app/logger_config.py) for consistent logging format
- Uses `colorlog` for colored console output with specific format: `'%(asctime)s - %(name)s - %(log_color)s%(levelname)s%(reset)s - %(message)s'`
- Logger names follow module hierarchy with `job_agent` as root logger
- Browser-use logger is explicitly set to INFO level

### Error Handling
- Job fit analysis defaults to `is_fit=True` when errors occur to avoid blocking applications
- Resume ranking falls back to first resume when parsing errors occur
- Knowledge base returns "No relevant information found" message rather than empty results