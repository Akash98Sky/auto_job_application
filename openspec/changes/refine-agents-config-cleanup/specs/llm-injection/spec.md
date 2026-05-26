## ADDED Requirements

### Requirement: Flexible Model Injection in Agents
The `JobSearchAgent` and `JobApplicationAgent` classes MUST accept an optional pre-configured `llm` model instance in their constructor signatures.

#### Scenario: Mock LLM Injection in Testing
- **WHEN** a mock `BaseChatModel` is passed during agent creation
- **THEN** the agent SHALL use the provided mock instance for its operations instead of instantiating a new one.

### Requirement: Standard LLM Instantiation Fallback
If the optional `llm` constructor parameter is not provided or is set to None, the agents SHALL fallback to instantiating the default ChatOpenAI instance using configured NVIDIA values.

#### Scenario: Fallback Instantiation
- **WHEN** an agent is instantiated with `llm=None`
- **THEN** it SHALL successfully initialize with the standard default NVIDIA configuration.
