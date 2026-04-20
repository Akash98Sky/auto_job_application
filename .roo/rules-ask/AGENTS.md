# Project Documentation Rules (Non-Obvious Only)

- Knowledge base files are stored in `user_data/knowledge_base/` (`.txt` or `.md` files only)
- Resume PDFs must be stored in `user_data/resumes/` directory
- Profile directory for browser automation is `./profile` with `Default` profile name
- Test files require project root path insertion: `sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))`
- Browser executable path defaults to Edge on Windows: `"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"`