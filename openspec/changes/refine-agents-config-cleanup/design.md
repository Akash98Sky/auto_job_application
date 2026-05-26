## Context

The system has several critical reliability gaps:
1. Configuration parameters (such as API keys) are not checked on startup, leading to downstream failure modes that are hard to diagnose.
2. Agents construct their own LLM client objects inside their initializers, leading to tight coupling that hinders unit test mocking.
3. Active browser sessions can easily escape and remain orphaned in system memory if the parent Python process exits abruptly without completing `finally` blocks.

## Goals / Non-Goals

**Goals:**
* Define `validate_config()` in `app/config.py` that checks for required environment variables and call it during the application's boot stage in `main.py`.
* Allow optional `llm` parameters in `JobSearchAgent` and `JobApplicationAgent` to enable direct dependency injection.
* Hook Python's `atexit` inside `SessionPool` to guarantee complete, synchronous process killing of all active browsers.

**Non-Goals:**
* Creating an external config manager service.
* Rewriting browser pooling architectures.
* Restructuring local database operations.

## Decisions

### 1. Fail-Fast Validation inside `main.py` rather than on `config.py` Import
* **Decision**: We will define `validate_config(raise_on_error=True)` inside `app/config.py` but will ONLY execute it automatically during standard runtime application startup in `main.py`.
* **Rationale**: If we execute validation automatically on importing `config.py`, all unit tests running in keyless environments (like standard CI pipelines or standard mocked test runners) will fail instantly. Calling it inside `main()` shields unit tests while providing robust fail-fast safety for production runs.

### 2. Dependency Injection for LLMs
* **Decision**: Modify the `JobSearchAgent` and `JobApplicationAgent` constructors to accept `llm: BaseChatModel | None = None`. If provided, use it directly.
* **Rationale**: This makes testing highly modular. We can inject a mock `BaseChatModel` directly in tests rather than using complex monkeypatching of the LLM imports.

### 3. Synchronous Process Cleanups inside `atexit`
* **Decision**: Implement a synchronous `close_all_sync()` handler in `SessionPool` registered via `atexit`. It will check if an asyncio loop is active and synchronously run the browser's async `kill()` methods or create immediate tasks.
* **Rationale**: `atexit` callbacks must be synchronous. Spawning synchronous event loop tasks inside the handler ensures we terminate Edge/Chrome processes even on unexpected exits.

## Risks / Trade-offs

* **[Risk]** Spawning `asyncio.run` inside `atexit` might throw loop errors if a loop is already closing.
  * **Mitigation**: Wrap the `b.kill()` execution in a nested try/except block that falls back to process-level checks or silences minor cleanup warnings.
