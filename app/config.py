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

# Model Configuration
AGENT_MODEL_NAME = os.getenv("AGENT_MODEL_NAME", "meta-llama/llama-4-scout-17b-16e-instruct")
MEM0_MODEL_NAME = os.getenv("MEM0_MODEL_NAME", "openai/gpt-oss-120b")
RESUME_MODEL_NAME = os.getenv("RESUME_MODEL_NAME", "llama-3.1-8b-instant")
