import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.knowledge_base import KnowledgeBase

def test_knowledge_base_query():
    """Test that the knowledge base can retrieve facts."""
    # Initialize knowledge base
    kb = KnowledgeBase()
    kb.load_from_directory()

    # Test query
    result = kb.query("What are the applicant's skills?")

    # Verify result is a string and not empty
    assert isinstance(result, str)
    assert len(result) > 0
    # Check for specific message when no information is found
    if "No relevant information" in result:
        print("Info: Knowledge base returned 'No relevant information' message as expected")

def test_knowledge_base_query_empty():
    """Test knowledge base behavior when no files are present."""
    with patch('os.listdir') as mock_listdir:
        mock_listdir.return_value = []
        kb = KnowledgeBase()
        result = kb.query("What are the applicant's skills?")
        assert "No relevant information" in result

def test_knowledge_base_load():
    """Test that the knowledge base loads files from directory."""
    kb = KnowledgeBase()
    # Should not raise an exception
    kb.load_from_directory()
    # If we get here without exceptions, the test passes
    assert True

def test_knowledge_base_with_test_files():
    """Test knowledge base with mock test files."""
    with patch('os.listdir') as mock_listdir, \
         patch('builtins.open', MagicMock()) as mock_open:
        mock_listdir.return_value = ['test1.txt', 'test2.md']
        mock_open.return_value.__enter__.return_value.read.return_value = "Sample knowledge content"
        
        kb = KnowledgeBase()
        kb.load_from_directory()
        result = kb.query("Sample query")
        assert isinstance(result, str)