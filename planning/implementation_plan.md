# Implementation Plan - Autonomous Job Application Agent

## Goal Description

Create an autonomous agent that searches for jobs and fills applications using `browser-use` for navigation and `mem0` for managing applicant knowledge. The agent will intelligently select the best resume from a local collection and answer application questions using its knowledge base.

## User Review Required

> [!IMPORTANT]
> - **Mem0 Configuration**: Need to ensure `mem0` is properly configured (APIs/Encryption if needed).
> - **Target Sites**: The generic `browser-use` agent captures varied forms, but specific logic might be needed for complex sites (e.g., Workday, LinkedIn). We will start with a general approach.
> - **Resume Parsing**: Basic text extraction will be used. Formatting preservation in upload is automatic (file upload), but content matching relies on text.

## Proposed Changes

### Dependencies

- Project management and execution MUST rely on `uv`. Do not use `pip` or `python` directly (e.g., use `uv run app/main.py`, `uv add package_name`).
- Add `mem0ai` implementation.
- Add `pypdf` for resume text extraction.
- Add `langchain` / `langchain-community` for LLM orchestration and ranking.
- Add `langchain-groq` for Groq model support.
- Add `langchain-cohere` for embeddings and reranking.
- Add `pydantic` for structured output from LLMs.

### Structured Output

- All LLM interactions that require structured data (e.g., job matching, resume ranking, form field extraction) MUST use Pydantic models.
- Use `with_structured_output()` method in LangChain to enforce response schemas.
- Define schemas in `app/models/` directory (e.g., `llm_responses.py`).

### Core Components

#### [UPDATED] [knowledge_base.py](app/knowledge_base.py)

- `KnowledgeBase` class.
- Uses `mem0` to store applicant details with Qdrant vector store and Cohere embeddings.
- `load_from_directory()`: Reads `.txt` and `.md` files from `user_data/knowledge_base`.
- `query(question)`: Retrieves relevant facts.

#### [UPDATED] [resume_manager.py](app/resume_manager.py)

- `ResumeManager` class.
- `load_resumes()`: Scans PDF files from `user_data/resumes`.
- `get_best_resume(job_description)`: Ranks resumes using LLM (Groq) against the job description.

#### [UPDATED] [job_agent.py](app/job_agent.py)

- `JobApplicationAgent` orchestrator.
- [x] `apply_to_job(job_url)`:
    1. Extracts job description using a separate agent pass.
    2. Selects best resume.
    3. Runs application agent with `query_knowledge_base` tool.
- [ ] `run_job_search(query)`: (TO BE IMPLEMENTED) Use `browser-use` to find job listings on LinkedIn, Indeed, etc.
- [ ] `analyze_job_fit(job_description)`: (TO BE IMPLEMENTED) Use LLM to determine if the job matches applicant's profile before applying.

#### [MODIFY] [main.py](main.py)

- Current: Hardcoded job URL for testing.
- Future: Add interactive CLI to search and apply, or run in a loop from a search query.

## Verification Plan

### Automated Tests

- [ ] `tests/test_knowledge_base.py`: Verify fact retrieval.
- [ ] `tests/test_resume_manager.py`: Verify ranking logic.

### Manual Verification

1. **Resume Selection**: (Completed)
    - Verify the correct resume is chosen for different job descriptions.
2. **Knowledge Retrieval**: (Completed)
    - Verify facts are correctly retrieved during form filling.
3. **End-to-End**: (In Progress)
    - Run against various application forms (Greenhouse, Lever, etc.).
