# Implementation Plan - Autonomous Job Application Agent

## Goal Description

Create an autonomous agent that searches for jobs and fills applications using `browser-use` for navigation and `mem0` for managing applicant knowledge. The agent will intelligently select the best resume from a local collection and answer application questions using its knowledge base.

## User Review Required
>
> [!IMPORTANT]
>
> - **Mem0 Configuration**: Need to ensure `mem0` is properly configured (APIs/Encryption if needed).
> - **Target Sites**: The generic `browser-use` agent captures varied forms, but specific logic might be needed for complex sites (e.g., Workday, LinkedIn). We will start with a general approach.
> - **Resume Parsing**: Basic text extraction will be used. Formatting preservation in upload is automatic (file upload), but content matching relies on text.

## Proposed Changes

### Dependencies

- Add `mem0ai` implementation.
- Add `pypdf` for resume text extraction.
- Add `langchain` / `langchain-community` if required for advanced matching (optional for now).

### Core Components

#### [NEW] [knowledge_base.py](file:///d:/Programming/Python/auto_job_application/knowledge_base.py)

- `KnowledgeBase` class.
- Uses `mem0` to store applicant details.
- `load_from_directory(path)`: Reads txt/md/json files from `user_data/knowledge_base` and adds to mem0.
- `query(question)`: Retrieves relevant info for form filling.

#### [NEW] [resume_manager.py](file:///d:/Programming/Python/auto_job_application/resume_manager.py)

- `ResumeManager` class.
- `load_resumes(path)`: Scans PDF files.
- `get_best_resume(job_description)`: Returns the path of the most relevant resume.
  - *Logic*: Extract text from all resumes, use LLM to rank them against the job description.

#### [NEW] [job_agent.py](file:///d:/Programming/Python/auto_job_application/job_agent.py)

- Orchestrator class.
- Initializes `Browser` and `Agent` (from `browser-use`).
- `run_job_search(query)`: Finds jobs.
- `apply_to_job(job_url)`:
    1. Extract page content.
    2. Select resume via `ResumeManager`.
    3. Loop through form fields:
        - Query `KnowledgeBase` for answers.
        - Fill using `browser-use`.

#### [MODIFY] [main.py](file:///d:/Programming/Python/auto_job_application/main.py)

- Update to use the new `JobApplicationAgent` structure instead of the simple example.
- Add CLI args or interactive mode to trigger specific tasks.

## Verification Plan

### Automated Tests

- None currently exist.
- We will rely on manual verification as this is a browser automation task.

### Manual Verification

1. **Resume Selection**:
    - Place 2 distinct resumes in `user_data/resumes`.
    - Run a mock selection against a specific job description.
    - Verify the correct resume is chosen.
2. **Knowledge Retrieval**:
    - Add a fact to `user_data/knowledge_base`.
    - Query the `KnowledgeBase` class and verify the answer.
3. **End-to-End**:
    - Run the agent against a simple application form (or a controlled google form/test site).
    - Verify fields are filled correctly.
