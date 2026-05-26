## Context

The current autonomous job application agent system has grown into separate components that duplicate logic and lack unified structure. Because there is no standard base agent, error handling, logging configuration, and API standardizations are done in an ad-hoc manner. Furthermore, the use of `mem0` with a global Qdrant instance location (`/tmp/qdrant`) results in severe file locking and permission issues when running multiple operations or unit tests concurrently.

## Goals / Non-Goals

**Goals:**
* Define and implement a `BaseAgent` class to standardize logger loading, LLM instantiation, and base lifecycles.
* Isolate Qdrant database storage paths to each agent's local `data_dir` to prevent concurrent instance file locks.
* Establish standard docstrings and type annotations across all public APIs for readability and autogeneration.
* Standardize cleanup mechanisms in `SessionPool` and `BaseAgent` subclasses to avoid memory/process leaks.
* Fix failing test cases by ensuring mock setups match actual implementations (e.g., mocking `pathlib.Path.glob` instead of `os.listdir`).

**Non-Goals:**
* Modifying the core algorithms of the NVIDIA job-search LLM or Groq resume selection templates.
* Rewriting the `browser-use` library or replacement of `mem0`.
* Adding new user-facing features (focus is purely on architectural health, documentation, and test reliability).

## Decisions

### 1. Standardized `BaseAgent` Class
* **Decision**: Create an abstract/generic base class `BaseAgent` in `app/agents/base_agent.py` that all agents inherit from.
* **Rationale**: By inheriting from `BaseAgent`, individual agents share uniform setup logic for their loggers and default models, and acquire standard lifecycle methods like `close()`.
* **Alternatives Considered**: Keeping them independent and copying code. This was rejected due to high maintenance overhead and lack of unified resource control.

### 2. Isolated Qdrant Storage Location
* **Decision**: Configure the `mem0` vector store `provider="qdrant"` to use a local `path` isolated within each agent's configured `data_dir` (e.g., `self.data_dir / "qdrant"`).
* **Rationale**: This prevents concurrent database collisions on `/tmp/qdrant` and allows different environments/tests to run in parallel without `portalocker` access errors.
* **Alternatives Considered**: Using a running Docker Qdrant container. This was rejected to maintain a simple zero-dependency local setup.

### 3. Asynchronous Resource Cleanup and Lifecycle Standard
* **Decision**: Add an async `close()` method to `BaseAgent`. The subclasses (`JobApplicationAgent`, `JobSearchAgent`, etc.) will override this method to safely close active browsers or database connections.
* **Rationale**: Explicitly closing browser-use browser sessions and release-locks allows clean teardowns, preventing runaway browser processes and database locks.

### 4. Correct Test Mocking & Pytest-Asyncio Configuration
* **Decision**: Update pytest configuration and test files to mock `Path.glob` instead of `os.listdir` for `ResumeManagerAgent` tests, and provide isolated temp directory overrides during unit tests. Also, configure `pytest-asyncio` mode to `auto` or use explicit configuration to fix the `async def functions are not natively supported` errors.
* **Rationale**: Ensures tests are deterministic and do not touch real disk resumes or step on concurrent database instances.

## Risks / Trade-offs

* **[Risk]** Changing agent inheritance might break existing initializations in `main.py`.
  * **Mitigation**: Keep constructor signatures backward-compatible (e.g., allow passing custom dependencies or falling back to default values).
* **[Risk]** Existing local vector databases stored in `/tmp/qdrant` might need to be reloaded/re-indexed.
  * **Mitigation**: Automated checks can reload the local directory data upon initialization if the local qdrant database path does not exist.
