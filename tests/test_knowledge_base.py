import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.knowledge_base_agent import KnowledgeBaseAgent


def test_knowledge_base_agent_query():
    """Test that the knowledge base agent can retrieve facts."""
    # Initialize knowledge base
    kb = KnowledgeBaseAgent()
    kb.load_from_directory()

    # Test query
    result = kb.query("What are the applicant's skills?")

    # Verify result is a string and not empty
    assert isinstance(result, str)
    assert len(result) > 0
    # Check for specific message when no information is found
    if "No relevant information" in result:
        print("Info: Knowledge base returned 'No relevant information' message as expected")


def test_knowledge_base_agent_load():
    """Test that the knowledge base loads files from directory."""
    kb = KnowledgeBaseAgent()
    # Should not raise an exception
    kb.load_from_directory()
    # If we get here without exceptions, the test passes
    assert True


@pytest.mark.asyncio
async def test_knowledge_base_agent_query_mocked():
    """Test knowledge base query with mocked memory."""
    with patch('app.agents.knowledge_base_agent.Memory') as mock_memory_class:
        mock_memory = MagicMock()
        mock_memory.search.return_value = ["Skill: Python", "Skill: Django"]
        mock_memory_class.return_value = mock_memory

        kb = KnowledgeBaseAgent()
        result = kb.query("What are the applicant's skills?")

        assert isinstance(result, str)
        assert "Skill: Python" in result
        mock_memory.search.assert_called_once_with("What are the applicant's skills?", user_id="applicant", limit=5)


def test_knowledge_base_agent_with_empty_search():
    """Test knowledge base when search returns empty results."""
    with patch('app.agents.knowledge_base_agent.Memory') as mock_memory_class:
        mock_memory = MagicMock()
        mock_memory.search.return_value = []
        mock_memory_class.return_value = mock_memory

        kb = KnowledgeBaseAgent()
        result = kb.query("Some query")

        assert "No relevant information" in result
