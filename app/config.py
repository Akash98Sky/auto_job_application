import os
from dotenv import load_dotenv

load_dotenv()

# Data Directories
KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR", "user_data/knowledge_base")
RESUMES_DIR = os.getenv("RESUMES_DIR", "user_data/resumes")

# Browser Configuration
BROWSER_EXECUTABLE_PATH = os.getenv("BROWSER_EXECUTABLE_PATH", "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe")
BROWSER_USER_DATA_DIR = os.getenv("BROWSER_USER_DATA_DIR", "./profile")
BROWSER_PROFILE_DIR = os.getenv("BROWSER_PROFILE_DIR", "Default")

# Groq Model Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
BROWSER_AGENT_GROQ_MODEL = os.getenv("BROWSER_AGENT_GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
RESUME_AGENT_GROQ_MODEL = os.getenv("RESUME_AGENT_GROQ_MODEL", "llama-3.1-8b-instant")
MEM0_LLM_GROQ_MODEL = os.getenv("MEM0_LLM_GROQ_MODEL", "openai/gpt-oss-120b")

# Cohere Model Configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
MEM0_EMBED_COHERE_MODEL = os.getenv("MEM0_EMBED_COHERE_MODEL", "embed-v4.0")
MEM0_RERANK_COHERE_MODEL = os.getenv("MEM0_RERANK_COHERE_MODEL", "rerank-v4.0-fast")

# Nvidia AI Endpoints Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1/"
BROWSER_AGENT_NVIDIA_MODEL = os.getenv("BROWSER_AGENT_NVIDIA_MODEL", "qwen/qwen3.5-122b-a10b")

def validate_config(raise_on_error: bool = True) -> bool:
    """
    Validates that all essential API keys are present and non-empty.

    Args:
        raise_on_error (bool): If True, raises a ValueError on validation failure.
                              If False, logs critical warnings instead.

    Returns:
        bool: True if configuration is valid, False otherwise.

    Raises:
        ValueError: If a required API key is missing and raise_on_error is True.
    """
    missing_keys = []
    if not NVIDIA_API_KEY:
        missing_keys.append("NVIDIA_API_KEY")
    if not GROQ_API_KEY:
        missing_keys.append("GROQ_API_KEY")
    if not COHERE_API_KEY:
        missing_keys.append("COHERE_API_KEY")

    if missing_keys:
        msg = (
            f"Configuration validation failed! The following required environment variables "
            f"are missing or empty: {', '.join(missing_keys)}. "
            f"Please configure them in your .env file or environment."
        )
        if raise_on_error:
            raise ValueError(msg)
        return False
    return True