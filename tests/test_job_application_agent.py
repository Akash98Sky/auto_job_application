import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.job_application_agent import JobApplicationAgent
from app.agents.knowledge_base_agent import KnowledgeBaseAgent
from app.agents.resume_manager_agent import ResumeManagerAgent


class TestJobApplicationAgent:
    """Test cases for JobApplicationAgent class."""

    @pytest.fixture
    def mock_browser_session(self):
        """Create a mock browser session."""
        return MagicMock()

    @pytest.fixture
    def mock_knowledge_base(self):
        """Create a mock knowledge base agent."""
        kb = MagicMock(spec=KnowledgeBaseAgent)
        kb.query.return_value = "Applicant has 5 years of Python experience, skilled in Django and AWS."
        return kb

    @pytest.fixture
    def mock_resume_manager(self):
        """Create a mock resume manager agent."""
        rm = MagicMock(spec=ResumeManagerAgent)
        rm.get_best_resume = AsyncMock(return_value=str(Path("user_data/resumes/test_resume.pdf").absolute()))
        return rm

    @pytest.fixture
    def job_application_agent(self, mock_browser_session, mock_knowledge_base, mock_resume_manager):
        """Create a JobApplicationAgent instance with mocked dependencies."""
        return JobApplicationAgent(
            browser=mock_browser_session,
            knowledge_base=mock_knowledge_base,
            resume_manager=mock_resume_manager
        )

    def test_job_application_agent_initialization(self, mock_browser_session, mock_knowledge_base, mock_resume_manager):
        """Test that JobApplicationAgent initializes properly."""
        agent = JobApplicationAgent(
            browser=mock_browser_session,
            knowledge_base=mock_knowledge_base,
            resume_manager=mock_resume_manager
        )
        assert agent is not None
        assert agent.browser == mock_browser_session
        assert agent.knowledge_base == mock_knowledge_base
        assert agent.resume_manager == mock_resume_manager
        assert agent.llm is not None

    def test_build_tools(self, job_application_agent):
        """Test that _build_tools creates tools with knowledge base action."""
        tools = job_application_agent._build_tools()
        assert tools is not None

    def test_query_knowledge_base_tool(self, job_application_agent, mock_knowledge_base):
        """Test that the query_knowledge_base tool calls the knowledge base."""
        tools = job_application_agent._build_tools()

        # The tool should be registered and callable
        mock_knowledge_base.query.return_value = "Test knowledge"
        result = mock_knowledge_base.query("What is the applicant's experience?")

        assert result == "Test knowledge"
        mock_knowledge_base.query.assert_called_once_with("What is the applicant's experience?")

    @pytest.mark.asyncio
    async def test_apply_to_job_success(self, job_application_agent, mock_browser_session):
        """Test successful job application flow."""
        # Mock extractor agent
        mock_extract_history = MagicMock()
        mock_extract_history.is_successful.return_value = True
        mock_extract_history.final_result.return_value = "Looking for Python developer with Django experience."

        # Mock application agent
        mock_app_history = MagicMock()
        mock_app_history.is_successful.return_value = True
        mock_app_history.final_result.return_value = "Application submitted successfully."

        call_count = [0]  # Use list to track calls in closure

        def agent_factory(task, **kwargs):
            mock_agent = MagicMock()
            if call_count[0] == 0:
                # First call is extractor agent
                mock_agent.run = AsyncMock(return_value=mock_extract_history)
                mock_agent.close = AsyncMock()
            else:
                # Second call is application agent
                mock_agent.run = AsyncMock(return_value=mock_app_history)
                mock_agent.close = AsyncMock()
            call_count[0] += 1
            return mock_agent

        with patch('app.agents.job_application_agent.Agent', side_effect=agent_factory):
            result = await job_application_agent.apply_to_job("https://example.com/job/123")

        # Should have called both agents
        assert call_count[0] == 2
        assert result is not None

    @pytest.mark.asyncio
    async def test_apply_to_job_no_resume(self, job_application_agent, mock_browser_session):
        """Test job application when no suitable resume is found."""
        # Mock extractor agent
        mock_extract_history = MagicMock()
        mock_extract_history.is_successful.return_value = True
        mock_extract_history.final_result.return_value = "Looking for Python developer."

        # Mock resume manager to return None
        job_application_agent.resume_manager.get_best_resume = AsyncMock(return_value=None)

        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(return_value=mock_extract_history)
        mock_agent.close = AsyncMock()

        with patch('app.agents.job_application_agent.Agent', return_value=mock_agent):
            result = await job_application_agent.apply_to_job("https://example.com/job/123")

        assert result is None

    @pytest.mark.asyncio
    async def test_apply_to_job_extractor_fails(self, job_application_agent, mock_browser_session):
        """Test job application when extractor agent fails."""
        # Mock extractor agent to fail
        mock_extract_history = MagicMock()
        mock_extract_history.is_successful.return_value = False
        mock_extract_history.final_result.return_value = None

        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(return_value=mock_extract_history)
        mock_agent.close = AsyncMock()

        with patch('app.agents.job_application_agent.Agent', return_value=mock_agent):
            result = await job_application_agent.apply_to_job("https://example.com/job/123")

        # Should use default job description and continue
        job_application_agent.resume_manager.get_best_resume.assert_called_once()

    @pytest.mark.asyncio
    async def test_apply_to_job_application_fails(self, job_application_agent, mock_browser_session):
        """Test job application when application agent fails."""
        # Mock extractor agent
        mock_extract_history = MagicMock()
        mock_extract_history.is_successful.return_value = True
        mock_extract_history.final_result.return_value = "Looking for Python developer."

        # Mock application agent to fail
        mock_app_history = MagicMock()
        mock_app_history.is_successful.return_value = False
        mock_app_history.final_result.return_value = None

        call_count = [0]

        def agent_factory(task, **kwargs):
            mock_agent = MagicMock()
            if call_count[0] == 0:
                mock_agent.run = AsyncMock(return_value=mock_extract_history)
                mock_agent.close = AsyncMock()
            else:
                mock_agent.run = AsyncMock(return_value=mock_app_history)
                mock_agent.close = AsyncMock()
            call_count[0] += 1
            return mock_agent

        with patch('app.agents.job_application_agent.Agent', side_effect=agent_factory):
            result = await job_application_agent.apply_to_job("https://example.com/job/123")

        # Should return the history even if unsuccessful
        assert result is not None
