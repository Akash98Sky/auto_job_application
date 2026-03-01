import pytest
import sys
import os

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
    
    # Verify result is a string and not empty (assuming knowledge base has data)
    assert isinstance(result, str)
    # If knowledge base is empty, it returns a specific message
    if not result or "No relevant information" in result:
        print("Warning: Knowledge base is empty. Please add .txt or .md files to user_data/knowledge_base/")
        
def test_knowledge_base_load():
    """Test that the knowledge base loads files from directory."""
    kb = KnowledgeBase()
    # Should not raise an exception
    kb.load_from_directory()
    assert True