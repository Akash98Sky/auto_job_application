## ADDED Requirements

### Requirement: Mandatory Environment Key Verification
The configuration system MUST verify that all essential environment API keys (`NVIDIA_API_KEY`, `GROQ_API_KEY`, `COHERE_API_KEY`) are present and non-empty during initialization.

#### Scenario: Key Missing Startup Failure
- **WHEN** config is imported and `NVIDIA_API_KEY` is missing
- **THEN** it SHALL raise a descriptive ValueError explaining which key is absent.
