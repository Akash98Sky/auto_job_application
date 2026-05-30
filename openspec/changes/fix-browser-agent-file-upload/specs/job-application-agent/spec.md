## ADDED Requirements

### Requirement: JobApplicationAgent collects and provides resume file paths to browser agents
The JobApplicationAgent SHALL automatically discover all resume PDF files in the `user_data/resumes/` directory during initialization and convert them to absolute paths. These paths SHALL be passed to all created browser agents via the `available_file_paths` parameter.

#### Scenario: Agent initializes with available resumes
- **WHEN** JobApplicationAgent is initialized with access to the resumes directory
- **THEN** it collects all `.pdf` files from `user_data/resumes/` and stores absolute paths

#### Scenario: Extractor agent receives available file paths
- **WHEN** the job description extraction agent is created inside `apply_to_job()`
- **THEN** it is initialized with `available_file_paths` containing all discovered resume files

#### Scenario: Application agent receives available file paths
- **WHEN** the job application agent is created for form completion
- **THEN** it is initialized with `available_file_paths` containing all discovered resume files

#### Scenario: No resumes found in directory
- **WHEN** the `user_data/resumes/` directory is empty or doesn't exist
- **THEN** JobApplicationAgent logs a warning but initializes successfully with an empty `available_file_paths` list

### Requirement: File paths must be resolved to absolute paths
The JobApplicationAgent SHALL resolve all resume file paths to absolute paths using cross-platform path resolution. On Windows, paths SHALL use the system's native path separators.

#### Scenario: Path resolution on Windows
- **WHEN** a resume file `AkashMondal_Cv26.2.pdf` exists in `user_data/resumes/`
- **THEN** it is resolved to an absolute path like `D:\\Programming\\Python\\auto_job_application\\user_data\\resumes\\AkashMondal_Cv26.2.pdf`

#### Scenario: Resume file upload uses provided path
- **WHEN** ResumeManagerAgent selects a resume file for a job application
- **THEN** the application agent can successfully upload that file because its path is in `available_file_paths`

#### Scenario: File not found error is prevented
- **WHEN** the application agent attempts to upload a resume file that was in `available_file_paths` at init time
- **THEN** the upload succeeds and no "File path is not available" error occurs
