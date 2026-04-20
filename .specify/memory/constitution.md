<!--
SYNC IMPACT REPORT
Version: 1.0.0 -> 1.1.0
Modified Principles: Template defaults to Auto Job Application specific guidelines
Added Sections: None
Removed Sections: None
Templates Requiring Updates: ✅ templates verified
TODOs: None
-->
# Auto Job Application Constitution

## Core Principles

### I. Agent Architecture First
The project must rely on modular, single-responsibility agents utilizing the `browser-use` framework and LLM orchestrators (e.g., NVIDIA qwen, Groq) rather than low-level parsing libraries like Playwright or Selenium. Core agents include the Job Search, Job Application, Knowledge Base, and Resume Manager agents.

### II. Memory & Context Integration
The `mem0` framework with `Qdrant` vector store must handle applicant context. All file-based operations for knowledge constraints and resumes must be confined safely to the `user_data/knowledge_base/` and `user_data/resumes/` directories. 

### III. System Configuration Consistency
All environment configurations, external tool parameters, and provider credentials must be routed centrally through `app/config.py` utilizing `python-dotenv`. Explicit environmental fallbacks are mandatory.

### IV. Graceful Error Handling & Fallbacks
Agent evaluations such as job fits, resume ranking, and knowledge base queries must implement try/except mechanisms resolving to default fallback behaviors (e.g., `is_fit=True`, returning "No knowledge base info" strings, fallback single-resume selection) to ensure uninterrupted multi-step agent processes.

### V. Testing & Observability Rigor
Comprehensive async test integration via `pytest` mimicking LLM behavior with mock objects is required. Custom multi-colored console logs using `app/logger_config.py` (`get_logger`) must be used at the module-level instead of bare prints to unify systemic observability.

## Technologies & Stack

- **Browser Automation**: `browser-use`
- **Memory Framework**: `mem0ai` with `Qdrant`
- **LLM APIs**: `langchain-cohere`, `ChatOpenAI` endpoints for NVIDIA, Groq
- **Testing**: `pytest`, with `pytest-asyncio`
- **Logging**: `colorlog`

## Governance

All PRs/reviews must verify compliance with the Agent Architecture rules outlined in `AGENTS.md`. No new agents can be merged without corresponding test coverage and dependency additions integrated into `app/config.py` and `pyproject.toml`.

**Version**: 1.1.0 | **Ratified**: 2026-04-20 | **Last Amended**: 2026-04-20
