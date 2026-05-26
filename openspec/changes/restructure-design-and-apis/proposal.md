## Why

The current implementation of the autonomous job application agents faces several architectural limitations:
1. **Lack of Standardized Agent Design**: There is no base agent structure. Each agent (`JobSearchAgent`, `JobApplicationAgent`, `KnowledgeBaseAgent`, `ResumeManagerAgent`) independently manages its own configurations, LLM clients, loggers, and lifecycles, leading to code duplication and inconsistent behavior.
2. **Resource Management Issues**: Database and browser resources are not properly closed or cleaned up. Specifically, the local Qdrant instance in the `KnowledgeBaseAgent` holds persistent file locks, causing parallel tests and concurrent operations to fail with access/lock errors.
3. **Weak Mocking & Test Execution**: Unit tests mock unrelated standard library functions (e.g., mocking `os.listdir` when the implementation uses `pathlib.Path.glob`), resulting in brittle tests that fail on different environments or load real files.
4. **Poor API Documentation**: The public APIs lack standard docstrings and clean typings, making integration, maintenance, and expansion difficult.

Restructuring the codebase now is critical to support scalability, allow reliable concurrent operations, improve test coverage, and document the public interfaces clearly for development.

## What Changes

We will introduce a clean, structured base agent architecture, unify resource lifecycles, add proper cleanup mechanisms, fix failing test cases, and document all public APIs.

* **Base Agent Architecture**:
  * Introduce a `BaseAgent` class in `app/agents/base_agent.py` to centralize logging setup, LLM configuration, and resource cleanups.
  * Update all four child agents to inherit from `BaseAgent` and reuse its shared configurations.
* **Unified Resource Lifecycle & Proper Cleanup**:
  * Add explicit initialization and cleanup (`close()`) methods in `KnowledgeBaseAgent` and `SessionPool` to release active database locks and browser sessions correctly.
  * Standardize error handling across all public methods.
* **API Documentation**:
  * Write consistent, detailed docstrings (Google/Sphinx style) for all public functions, classes, and properties.
  * Enhance Pydantic model usage for structured outputs and clear schema definitions.
* **Robust Test Environment**:
  * Fix the test mocking strategy in `tests/test_resume_manager.py` by patching `pathlib.Path.glob`.
  * Resolve concurrent Qdrant resource collisions in `tests/test_knowledge_base.py` by using separate temporary storage directories for testing.
  * Configure `pytest-asyncio` correctly for async test functions.

## Capabilities

### New Capabilities
- `agent-architecture`: Establishes the core agent architectural contract, defining standard base classes, lifecycle methods, error patterns, and the public API interfaces of the agents.
- `browser-session-management`: Defines how browser instances are dynamically pooled, configured, reused, and terminated across multiple operations.

### Modified Capabilities
<!-- None currently exist as openspec/specs/ is empty. -->

## Impact

* **Impacted Code**:
  * `app/agents/job_search_agent.py`
  * `app/agents/job_application_agent.py`
  * `app/agents/knowledge_base_agent.py`
  * `app/agents/resume_manager_agent.py`
  * `app/session_pool.py`
  * `main.py`
* **Impacted Tests**:
  * `tests/test_knowledge_base.py`
  * `tests/test_resume_manager.py`
  * `tests/test_job_search_agent.py`
  * `tests/test_job_application_agent.py`
* **Dependencies**:
  * Added `pytest-asyncio` dependency to `pyproject.toml` if missing or configure `pytest` to support async natively using suitable arguments or plugins.
