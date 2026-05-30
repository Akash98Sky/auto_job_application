## Context

The `JobApplicationAgent` uses browser-use to automate job application workflows. It creates two separate agents:
1. **Extractor Agent**: Navigates to the job URL and extracts the job description
2. **Application Agent**: Fills the application form, uploads the resume, and queries the knowledge base

The browser-use library's file upload functionality requires explicit `available_file_paths` parameter during Agent initialization. The Application Agent already includes this parameter, but the Extractor Agent does not, leading to potential issues if the extractor agent needs to handle file operations.

## Goals / Non-Goals

**Goals:**
- Ensure all browser agents in the application workflow have access to required file paths
- Resolve file paths to absolute paths compatible with the browser-use library
- Make the solution robust on Windows systems (which use backslash path separators)
- Maintain backward compatibility with existing agent initialization patterns

**Non-Goals:**
- Add new file upload capabilities beyond resume uploads
- Modify the resume manager or resume selection logic
- Change the overall job application workflow structure

## Decisions

1. **File Path Resolution Strategy**: Use `pathlib.Path` to resolve the `user_data/resumes/` directory and enumerate all resume files. This provides cross-platform compatibility and handles relative paths correctly.

2. **Timing of Path Collection**: Collect available resume paths during `JobApplicationAgent.__init__()` rather than at job application time. This allows all agents to be aware of all available resumes from the start.

3. **Absolute Path Conversion**: Convert all resolved paths to absolute paths using `.resolve()` before passing to browser agents. The browser-use library expects absolute paths.

4. **Fallback Handling**: If the resumes directory doesn't exist or contains no files, initialize with an empty list. Log warnings to alert users of missing resumes, but don't fail agent initialization.

5. **Pass Paths to Both Agents**: Provide `available_file_paths` to both the extractor agent and application agent for consistency and future-proofing.

## Risks / Trade-offs

**Risk: Hard-coded resume directory path**
→ *Mitigation*: The `user_data/resumes/` directory path is already a project convention per AGENTS.md. If this changes, the configuration can be easily updated in `config.py`.

**Risk: File paths may change between initialization and upload**
→ *Mitigation*: This is an edge case (files deleted after agent initialization). Log a warning when collecting paths; if files are deleted later, the browser agent will still error appropriately.

**Risk: Windows path handling complexity**
→ *Mitigation*: Using `pathlib.Path` and `.resolve()` automatically handles Windows backslashes and UNC paths correctly.

**Trade-off: Memory overhead of keeping file paths in memory**
→ *Justification*: Minimal impact - typically only a few resume files (paths are small strings). Benefit of immediate availability outweighs the negligible memory cost.

## Implementation Approach

1. In `JobApplicationAgent.__init__()`:
   - Import `Path` from `pathlib`
   - Create a method `_collect_available_resumes()` that:
     - Resolves the `user_data/resumes/` path
     - Scans for `.pdf` files (existing convention)
     - Returns list of absolute path strings
   - Store available paths as instance variable `self.available_file_paths`

2. Update agent creation in `apply_to_job()`:
   - Pass `self.available_file_paths` to both extractor and application agents
   - Log the collected paths for debugging

3. Update `_build_tools()` if needed to ensure consistency (likely no changes needed as tools configuration is already clean)

## Migration Plan

- No user-facing changes required
- Existing job applications will work as before with improved reliability
- No rollback needed as this is purely additive (enabling currently broken functionality)
