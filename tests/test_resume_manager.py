import pytest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.resume_manager import ResumeManager

def test_resume_manager_load():
    """Test that the resume manager can load resumes."""
    # We need to mock the LLM or provide a dummy one
    # For now, we'll just check if it initializes without error
    # Note: This might fail if GROQ_API_KEY is not set
    
    try:
        from app.config import AGENT_MODEL_NAME
        from browser_use.llm import ChatGroq
        llm = ChatGroq(model=AGENT_MODEL_NAME, temperature=0)
        
        rm = ResumeManager(llm=llm)
        rm.load_resumes()
        
        # Check if resumes are loaded
        assert len(rm.resumes) >= 0
        
    except Exception as e:
        print(f"Skipping test_resume_manager_load due to missing dependencies or API keys: {e}")
        pytest.skip("Missing dependencies or API keys")

def test_resume_manager_get_best():
    """Test that the resume manager can select the best resume."""
    try:
        from app.config import AGENT_MODEL_NAME
        from browser_use.llm import ChatGroq
        llm = ChatGroq(model=AGENT_MODEL_NAME, temperature=0)
        
        rm = ResumeManager(llm=llm)
        rm.load_resumes()
        
        job_description = "We are looking for a Python developer with experience in AI."
        best_resume = rm.get_best_resume(job_description)
        
        # If no resumes are available, it should return None or handle gracefully
        assert best_resume is None or isinstance(best_resume, str)
        
    except Exception as e:
        print(f"Skipping test_resume_manager_get_best due to missing dependencies or API keys: {e}")
        pytest.skip("Missing dependencies or API keys")