## 1. Setup and Discovery

- [x] 1.1 Import `Path` from `pathlib` in JobApplicationAgent
- [x] 1.2 Create `_collect_available_resumes()` method to discover resume files

## 2. Resume Path Collection Implementation

- [x] 2.1 Implement resume directory discovery using `Path("user_data/resumes/")`
- [x] 2.2 Filter for `.pdf` files only in the resumes directory
- [x] 2.3 Resolve all paths to absolute paths using `Path.resolve()`
- [x] 2.4 Convert resolved paths to strings in a list
- [x] 2.5 Add logging to report collected resume paths
- [x] 2.6 Handle case where resumes directory doesn't exist (log warning, return empty list)
- [x] 2.7 Handle case where resumes directory exists but is empty (log warning, return empty list)

## 3. JobApplicationAgent Initialization

- [x] 3.1 Call `_collect_available_resumes()` in `__init__()` method
- [x] 3.2 Store result in instance variable `self.available_file_paths`
- [x] 3.3 Log the collected file paths for debugging

## 4. Update Agent Creation

- [x] 4.1 Update extractor_agent creation to pass `available_file_paths=self.available_file_paths`
- [x] 4.2 Verify application_agent already receives `available_file_paths` parameter
- [x] 4.3 Test that both agents receive the parameter correctly

## 5. Testing and Validation

- [x] 5.1 Verify resume files are found and paths are absolute
- [x] 5.2 Verify agents are initialized with correct file paths
- [x] 5.3 Test file upload during job application works without "File path is not available" error
- [x] 5.4 Test with empty resumes directory (warning logged, agents still initialize)
- [x] 5.5 Test with missing resumes directory (warning logged, agents still initialize)
