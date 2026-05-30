## ADDED Requirements

### Requirement: Browser agents can upload files using pre-declared paths
The browser-use Agent SHALL accept an `available_file_paths` parameter during initialization that declares which files the agent is permitted to upload. File paths SHALL be absolute paths to existing files on the system.

#### Scenario: Agent initializes with available file paths
- **WHEN** an Agent is created with `available_file_paths=["C:/path/to/file.pdf"]`
- **THEN** the Agent stores these paths internally for use during file upload operations

#### Scenario: Agent attempts to upload from declared path
- **WHEN** the Agent encounters a file upload form and tries to upload a file from the `available_file_paths` list
- **THEN** the browser automation completes successfully with the file uploaded

#### Scenario: Agent attempts to upload from undeclared path
- **WHEN** the Agent tries to upload a file that is NOT in the `available_file_paths` list
- **THEN** the Agent raises an error: "File path ... is not available"

### Requirement: File paths must be absolute and validated
All file paths in `available_file_paths` SHALL be absolute paths that exist on the system before Agent initialization. Paths SHALL use the system's native path separator (backslash on Windows, forward slash on Unix-like systems).

#### Scenario: Absolute path on Windows
- **WHEN** a Windows file path like `D:\\Programming\\Python\\auto_job_application\\user_data\\resumes\\resume.pdf` is provided
- **THEN** the Agent accepts it and uses it for file operations

#### Scenario: Relative path provided
- **WHEN** a relative path like `user_data/resumes/resume.pdf` is provided to an Agent
- **THEN** the Agent either rejects it or converts it to an absolute path based on current working directory

#### Scenario: Non-existent file path
- **WHEN** a path to a file that doesn't exist is provided to `available_file_paths`
- **THEN** the Agent may log a warning but continues initialization; the actual error occurs during upload attempt
