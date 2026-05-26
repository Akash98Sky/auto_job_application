## 1. Core Architecture

- [x] 1.1 Create `BaseAgent` class in `app/agents/base_agent.py` containing common setup and lifecycle hooks.
- [x] 1.2 Update `app/agents/__init__.py` to export `BaseAgent`.

## 2. Agent Restructuring & API Documentation

- [x] 2.1 Restructure `KnowledgeBaseAgent` to inherit from `BaseAgent`, implement isolated local Qdrant directory paths, add complete Google-style docstrings, and support lifecycle `close()`.
- [x] 2.2 Restructure `ResumeManagerAgent` to inherit from `BaseAgent` and add clean documentation and typings for all methods.
- [x] 2.3 Restructure `JobSearchAgent` to inherit from `BaseAgent` and fully document `search_and_filter_jobs`, `run_job_search`, and `analyze_job_fit`.
- [x] 2.4 Restructure `JobApplicationAgent` to inherit from `BaseAgent` and document the `apply_to_job` public method.

## 3. Session Pool & Entry Point Cleanups

- [x] 3.1 Document `SessionPool` methods and ensure safe process termination on close.
- [x] 3.2 Add proper close/cleanup handling in `main.py` to release active databases and browser sessions gracefully.

## 4. Test Infrastructure & Validation

- [x] 4.1 Fix `tests/test_resume_manager.py` by mocking `pathlib.Path.glob` instead of `os.listdir`.
- [x] 4.2 Fix `tests/test_knowledge_base.py` by using isolated temp directories for concurrent Qdrant test instances.
- [x] 4.3 Configure async tests support using `pytest-asyncio` settings in `pyproject.toml` or command line.
- [x] 4.4 Verify all unit tests pass without locking or async errors.
