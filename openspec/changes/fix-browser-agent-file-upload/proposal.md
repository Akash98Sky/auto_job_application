## Why

The browser-use library requires explicit `available_file_paths` parameter when creating agents that need to upload files. Currently, the `JobApplicationAgent` fails during resume uploads with error: "File path is not available." This is a critical blocker for automated job applications that require resume submissions.

## What Changes

- Update `JobApplicationAgent` initialization to collect available resume file paths from the `user_data/resumes/` directory
- Pass the `available_file_paths` parameter when creating browser agents in the agent initialization
- Ensure the file path resolution works correctly on Windows with backslash path separators
- Add fallback logic to handle cases where no resumes are found or paths cannot be resolved

## Capabilities

### New Capabilities
- `browser-agent-file-paths`: Enable browser agents to upload files by pre-declaring available file paths during agent initialization. This capability ensures file uploads in job application workflows work seamlessly.

### Modified Capabilities
- `job-application-agent`: Update initialization to pass resolved resume file paths to the underlying browser agent, fixing file upload functionality in job application submissions.

## Impact

- **Modified files**: `app/agents/job_application_agent.py`
- **Affected workflows**: Resume file uploads during job applications via browser automation
- **Dependencies**: No new external dependencies; uses existing `pathlib` for file resolution
- **Breaking changes**: None - this is a bug fix that enables previously broken functionality
