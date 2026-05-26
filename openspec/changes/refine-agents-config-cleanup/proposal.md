## Why

This proposal introduces key refinements to the autonomous job application system's stability, testability, and developer experience:
1. **Implicit Config Failures**: Currently, missing environment variables (such as `NVIDIA_API_KEY`, `GROQ_API_KEY`, or `COHERE_API_KEY`) lead to cryptic runtime crashes inside deep nested agent logic rather than failing fast at startup.
2. **Coupled LLM Initialization**: In `JobSearchAgent` and `JobApplicationAgent`, the LLM client is hardcoded and instantiated internally, creating high coupling and making mocking difficult during unit testing.
3. **Orphaned Browser Processes**: If the main process terminates abruptly (such as from a forced crash or interpreter fault), browser processes may bypass the `finally` cleanup block and remain orphaned in the background, consuming CPU and memory.

Addressing these issues improves the developer onboarding experience, makes writing tests significantly cleaner, and guarantees that no orphaned browser processes accumulate in system memory.

## What Changes

* **Fail-Fast Configuration Validation**:
  * Add automatic validation of critical API keys in `app/config.py`.
  * Stop execution immediately at startup with an informative message if required keys are missing or empty.
* **LLM Client Dependency Injection**:
  * Modify `JobSearchAgent` and `JobApplicationAgent` constructors to accept an optional `llm` model instance.
  * Update tests to directly pass mock models, eliminating imports patching.
* **Interpreter Exit Process Teardown**:
  * Integrate Python's `atexit` module into `SessionPool` to cleanly terminate and kill active browser sessions if the Python process shuts down or crashes.

## Capabilities

### New Capabilities
- `config-validation`: Establishes automatic fail-fast checks for required configurations and environment variables on boot.
- `llm-injection`: Defines the dependency injection contract for LLM instances in agents, improving unit test isolation.
- `orphan-process-cleanup`: Registers global interpreter lifecycle hooks to ensure all spawned browser processes are cleanly terminated under any exit path.

### Modified Capabilities
<!-- None -->

## Impact

* **Impacted Code**:
  * `app/config.py`
  * `app/session_pool.py`
  * `app/agents/job_search_agent.py`
  * `app/agents/job_application_agent.py`
* **Impacted Tests**:
  * `tests/test_job_search_agent.py`
  * `tests/test_job_application_agent.py`
