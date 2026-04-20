# Project Coding Rules (Non-Obvious Only)

## Build/Lint/Test Commands
- Run tests: `pytest`
- Run a single test file: `pytest tests/test_knowledge_base.py`
- Run a specific test: `pytest tests/test_knowledge_base.py::test_knowledge_base_query`

## Non-Obvious Coding Rules
- Always use the custom `get_logger()` function from [`app/logger_config.py`](app/logger_config.py) for consistent logging format
- Browser automation must use the `browser-use` library (not Playwright/Selenium) with the specific configuration from [`app/config.py`](app/config.py)
- Knowledge base queries must use `user_id="applicant"` metadata for proper context
- Resume ranking requires the specific prompt template format with "Resume ID" numbering
- Test files must include the project root path insertion: `sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))`
- When handling file paths, use `pathlib.Path` for cross-platform compatibility