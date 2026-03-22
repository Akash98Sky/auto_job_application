import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
import asyncio

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.resume_manager import ResumeManager

def test_resume_manager_initialization():
    """Test that the resume manager initializes properly."""
    with patch('app.resume_manager.ResumeManager.load_resumes') as mock_load:
        mock_llm = MagicMock()
        rm = ResumeManager(llm=mock_llm)
        assert rm is not None
        assert rm.llm == mock_llm
        mock_load.assert_called_once()

def test_resume_manager_load_no_resumes():
    """Test loading when no resumes are present."""
    with patch('os.listdir') as mock_listdir, \
         patch('app.config.RESUMES_DIR', Path("user_data/resumes")):
        mock_listdir.return_value = []
        mock_llm = MagicMock()
        
        rm = ResumeManager(llm=mock_llm)
        rm.load_resumes()
        
        assert len(rm.resumes) == 0

def test_resume_manager_load_with_resumes():
    """Test loading with mock resume files."""
    with patch('os.listdir') as mock_listdir, \
         patch('builtins.open', MagicMock()) as mock_open, \
         patch('app.config.RESUMES_DIR', Path("user_data/resumes")):
        mock_listdir.return_value = ['resume1.pdf', 'resume2.pdf']
        mock_open.return_value.__enter__.return_value.read.return_value = b"Mock PDF content"
        
        mock_llm = MagicMock()
        rm = ResumeManager(llm=mock_llm)
        rm.load_resumes()
        
        assert len(rm.resumes) == 2

@pytest.mark.asyncio
async def test_resume_manager_get_best_no_resumes():
    """Test get_best_resume when no resumes are available."""
    with patch('os.listdir') as mock_listdir:
        mock_listdir.return_value = []
        mock_llm = MagicMock()
        
        rm = ResumeManager(llm=mock_llm)
        rm.load_resumes()  # Load resumes to populate the resumes dict
        job_description = "We are looking for a Python developer with experience in AI."
        
        # Should raise ValueError when no resumes are loaded
        with pytest.raises(ValueError, match="No resumes loaded"):
            await rm.get_best_resume(job_description)

@pytest.mark.asyncio
async def test_resume_manager_get_best_single_resume():
    """Test get_best_resume when only one resume is available."""
    with patch('os.listdir') as mock_listdir, \
         patch('builtins.open', MagicMock()) as mock_open, \
         patch('app.resume_manager.PdfReader') as mock_pdf_reader:
        mock_listdir.return_value = ['resume1.pdf']
        mock_open.return_value.__enter__.return_value.read.return_value = b"Mock PDF content"
        
        # Mock PDF reader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample resume text"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        mock_llm = MagicMock()
        rm = ResumeManager(llm=mock_llm)
        rm.load_resumes()
        
        job_description = "We are looking for a Python developer with experience in AI."
        best_resume = await rm.get_best_resume(job_description)
        
        # Should return the path to the single resume
        assert Path(best_resume).name == "resume1.pdf"

@pytest.mark.asyncio
async def test_resume_manager_get_best_multiple_resumes():
    """Test get_best_resume when multiple resumes are available."""
    with patch('os.listdir') as mock_listdir, \
         patch('builtins.open', MagicMock()) as mock_open, \
         patch('app.resume_manager.PdfReader') as mock_pdf_reader:
        mock_listdir.return_value = ['resume1.pdf', 'resume2.pdf']
        mock_open.return_value.__enter__.return_value.read.return_value = b"Mock PDF content"
        
        # Mock PDF reader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample resume text"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        mock_llm = MagicMock()
        # Mock the LLM response for ranking
        mock_response = MagicMock()
        mock_response.completion = "1"  # Selects the second resume (ID 1)
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        
        rm = ResumeManager(llm=mock_llm)
        rm.load_resumes()
        
        job_description = "We are looking for a Python developer with experience in AI."
        best_resume = await rm.get_best_resume(job_description)
        
        # Should return the path to the selected resume
        assert Path(best_resume).name == "resume2.pdf"
        mock_llm.ainvoke.assert_called_once()
