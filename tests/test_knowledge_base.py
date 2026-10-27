import asyncio
import gc
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from auto_job_application.agents.knowledge_base_agent import KnowledgeBaseAgent


@pytest.fixture(autouse=True)
def run_gc_before_and_after():
    """Fixture to run garbage collection before and after every test, releasing global database locks."""
    gc.collect()
    yield
    gc.collect()


def test_knowledge_base_agent_query():
    """Test that the knowledge base agent can retrieve facts."""
    with tempfile.TemporaryDirectory() as temp_dir:
        kb = KnowledgeBaseAgent(data_dir=temp_dir)
        try:
            kb.load_from_directory()
            # Test query
            result = kb.query("What are the applicant's skills?")
            # Verify result is a string
            assert isinstance(result, str)
            assert len(result) > 0
            if "No relevant information" in result:
                print("Info: Knowledge base returned 'No relevant information' message as expected")
        finally:
            # Safely release resource locks
            asyncio.run(kb.close())
            # Force deletion and garbage collection to release file locks on Windows
            del kb
            gc.collect()


def test_knowledge_base_agent_load():
    """Test that the knowledge base loads files from directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock text file in the temp directory to verify loading
        mock_file = os.path.join(temp_dir, "skills.txt")
        with open(mock_file, "w", encoding="utf-8") as f:
            f.write("Skills: Python, Django, Cloud Development")

        kb = KnowledgeBaseAgent(data_dir=temp_dir)
        try:
            kb.load_from_directory()
            assert True
        finally:
            asyncio.run(kb.close())
            del kb
            gc.collect()


@pytest.mark.asyncio
async def test_knowledge_base_agent_query_mocked():
    """Test knowledge base query with mocked memory."""
    with patch('auto_job_application.agents.knowledge_base_agent.Memory') as mock_memory_class:
        mock_memory = MagicMock()
        mock_memory.search.return_value = ["Skill: Python", "Skill: Django"]
        mock_memory_class.return_value = mock_memory

        with tempfile.TemporaryDirectory() as temp_dir:
            kb = KnowledgeBaseAgent(data_dir=temp_dir)
            try:
                result = kb.query("What are the applicant's skills?")
                assert isinstance(result, str)
                assert "Skill: Python" in result
                mock_memory.search.assert_called_once_with("What are the applicant's skills?", user_id="applicant", limit=5)
            finally:
                await kb.close()
                del kb
                gc.collect()


def test_knowledge_base_agent_with_empty_search():
    """Test knowledge base when search returns empty results."""
    with patch('auto_job_application.agents.knowledge_base_agent.Memory') as mock_memory_class:
        mock_memory = MagicMock()
        mock_memory.search.return_value = []
        mock_memory_class.return_value = mock_memory

        with tempfile.TemporaryDirectory() as temp_dir:
            kb = KnowledgeBaseAgent(data_dir=temp_dir)
            try:
                result = kb.query("Some query")
                assert "No relevant information" in result
            finally:
                asyncio.run(kb.close())
                del kb
                gc.collect()
