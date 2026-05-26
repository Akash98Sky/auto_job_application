import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.resume_manager_agent import ResumeManagerAgent

def test_resume_manager_agent_initialization():
    """Test that the resume manager agent initializes properly."""
    mock_llm = MagicMock()
    with patch('app.agents.resume_manager_agent.ChatGroq'):
        rm = ResumeManagerAgent(llm=mock_llm)
        assert rm is not None
        assert rm.llm == mock_llm

def test_resume_manager_agent_load_no_resumes():
    """Test loading when no resumes are present."""
    with patch('pathlib.Path.glob') as mock_glob, \
         patch('app.agents.resume_manager_agent.RESUMES_DIR', Path("user_data/resumes")):
        mock_glob.return_value = []
        mock_llm = MagicMock()

        rm = ResumeManagerAgent(llm=mock_llm)
        rm.load_resumes()

        assert len(rm.resumes) == 0

def test_resume_manager_agent_load_with_resumes():
    """Test loading with mock resume files."""
    with patch('pathlib.Path.glob') as mock_glob, \
         patch('app.agents.resume_manager_agent.PdfReader') as mock_pdf_reader, \
         patch('app.agents.resume_manager_agent.RESUMES_DIR', Path("user_data/resumes")):
        
        mock_glob.return_value = [Path("user_data/resumes/resume1.pdf"), Path("user_data/resumes/resume2.pdf")]
        
        # Mock PDF reader pages
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Mock resume content"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader

        mock_llm = MagicMock()
        rm = ResumeManagerAgent(llm=mock_llm)
        rm.load_resumes()

        assert len(rm.resumes) == 2
        assert str(Path("user_data/resumes/resume1.pdf")) in rm.resumes
        assert str(Path("user_data/resumes/resume2.pdf")) in rm.resumes

@pytest.mark.asyncio
async def test_resume_manager_agent_get_best_no_resumes():
    """Test get_best_resume when no resumes are available."""
    with patch('pathlib.Path.glob') as mock_glob:
        mock_glob.return_value = []
        mock_llm = MagicMock()

        rm = ResumeManagerAgent(llm=mock_llm)
        rm.load_resumes()  # Dict will be empty
        job_description = "We are looking for a Python developer."

        with pytest.raises(ValueError, match="No resumes loaded"):
            await rm.get_best_resume(job_description)

@pytest.mark.asyncio
async def test_resume_manager_agent_get_best_single_resume():
    """Test get_best_resume when only one resume is available."""
    with patch('pathlib.Path.glob') as mock_glob, \
         patch('app.agents.resume_manager_agent.PdfReader') as mock_pdf_reader:
        mock_glob.return_value = [Path("user_data/resumes/resume1.pdf")]
        
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample resume text"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader

        mock_llm = MagicMock()
        rm = ResumeManagerAgent(llm=mock_llm)
        rm.load_resumes()

        job_description = "We are looking for a Python developer."
        best_resume = await rm.get_best_resume(job_description)

        assert Path(best_resume).name == "resume1.pdf"

@pytest.mark.asyncio
async def test_resume_manager_agent_get_best_multiple_resumes():
    """Test get_best_resume when multiple resumes are available."""
    with patch('pathlib.Path.glob') as mock_glob, \
         patch('app.agents.resume_manager_agent.PdfReader') as mock_pdf_reader:
        mock_glob.return_value = [Path("user_data/resumes/resume1.pdf"), Path("user_data/resumes/resume2.pdf")]
        
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample resume text"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.completion = "1"  # LLM selects second resume (index 1)
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        rm = ResumeManagerAgent(llm=mock_llm)
        rm.load_resumes()

        job_description = "We are looking for a Python developer."
        best_resume = await rm.get_best_resume(job_description)

        assert Path(best_resume).name == "resume2.pdf"
        mock_llm.ainvoke.assert_called_once()

@pytest.mark.asyncio
async def test_resume_manager_agent_get_best_llm_error():
    """Test get_best_resume handles LLM errors gracefully."""
    with patch('pathlib.Path.glob') as mock_glob, \
         patch('app.agents.resume_manager_agent.PdfReader') as mock_pdf_reader:
        mock_glob.return_value = [Path("user_data/resumes/resume1.pdf"), Path("user_data/resumes/resume2.pdf")]
        
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample resume text"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("LLM error"))

        rm = ResumeManagerAgent(llm=mock_llm)
        rm.load_resumes()

        job_description = "We are looking for a Python developer."
        best_resume = await rm.get_best_resume(job_description)

        # Falls back to the first resume on error
        assert Path(best_resume).name == "resume1.pdf"
