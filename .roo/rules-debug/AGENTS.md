# Project Debug Rules (Non-Obvious Only)

- Browser automation errors may fail silently - check browser logs carefully
- Knowledge base queries return "No relevant information found" rather than raising exceptions
- Resume ranking falls back to first resume when parsing errors occur
- Job fit analysis defaults to `is_fit=True` when errors occur to avoid blocking applications
- Test files may be skipped if API keys are missing - check test output for skip messages