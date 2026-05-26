## ADDED Requirements

### Requirement: Global Interpreter Shutdown Cleanup
The `SessionPool` class MUST register a global cleanup callback using Python's `atexit` module during its initialization.

#### Scenario: Graceful Termination on Abrupt Process Exit
- **WHEN** the Python interpreter exits or crashes
- **THEN** `SessionPool` SHALL immediately trigger a synchronous shutdown, closing and killing all active browser sessions.
