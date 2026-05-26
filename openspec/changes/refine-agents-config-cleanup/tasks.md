## 1. Config Validation

- [x] 1.1 Add `validate_config` validation function inside `app/config.py`.
- [x] 1.2 Call `validate_config` at startup in `main.py`'s `main` entry point.

## 2. LLM Dependency Injection

- [x] 2.1 Update `JobSearchAgent` in `app/agents/job_search_agent.py` to support optional LLM client injection.
- [x] 2.2 Update `JobApplicationAgent` in `app/agents/job_application_agent.py` to support optional LLM client injection.
- [x] 2.3 Refactor `tests/test_job_search_agent.py` to inject mock LLMs directly without import monkeypatching.
- [x] 2.4 Refactor `tests/test_job_application_agent.py` to inject mock LLMs directly without import monkeypatching.

## 3. Session Pool atexit Cleanup

- [x] 3.1 Integrate Python's `atexit` module and synchronous teardown hook in `SessionPool` inside `app/session_pool.py`.

## 4. Test Verification

- [x] 4.1 Execute `uv run pytest` and verify all tests pass cleanly.
