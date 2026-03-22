import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.job_search_agent import JobSearchAgent
from app.agents.knowledge_base_agent import KnowledgeBaseAgent
from app.models.llm_responses import JobFitAnalysis


class TestJobSearchAgent:
    """Test cases for JobSearchAgent class."""

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
    def job_search_agent(self, mock_browser_session, mock_knowledge_base):
        """Create a JobSearchAgent instance with mocked dependencies."""
        return JobSearchAgent(browser=mock_browser_session, knowledge_base=mock_knowledge_base)

    def test_job_search_agent_initialization(self, mock_browser_session, mock_knowledge_base):
        """Test that JobSearchAgent initializes properly."""
        agent = JobSearchAgent(browser=mock_browser_session, knowledge_base=mock_knowledge_base)
        assert agent is not None
        assert agent.browser == mock_browser_session
        assert agent.knowledge_base == mock_knowledge_base
        assert agent.llm is not None

    @pytest.mark.asyncio
    async def test_analyze_job_fit_good_fit(self, job_search_agent):
        """Test job fit analysis when the job is a good fit."""
        # Mock the LLM response
        mock_response = MagicMock()
        mock_response.completion = JobFitAnalysis(is_fit=True, reasoning="Skills match well.")

        with patch.object(job_search_agent.llm, 'ainvoke', AsyncMock(return_value=mock_response)):
            result = await job_search_agent.analyze_job_fit("Looking for Python developer with Django experience.")

        assert result.is_fit is True
        assert "Skills match" in result.reasoning

    @pytest.mark.asyncio
    async def test_analyze_job_fit_bad_fit(self, job_search_agent):
        """Test job fit analysis when the job is not a good fit."""
        # Mock the LLM response
        mock_response = MagicMock()
        mock_response.completion = JobFitAnalysis(is_fit=False, reasoning="Required skills do not match.")

        with patch.object(job_search_agent.llm, 'ainvoke', AsyncMock(return_value=mock_response)):
            result = await job_search_agent.analyze_job_fit("Looking for senior Java architect with 10 years experience.")

        assert result.is_fit is False
        assert "do not match" in result.reasoning

    @pytest.mark.asyncio
    async def test_analyze_job_fit_error_handling(self, job_search_agent):
        """Test that job fit analysis handles errors gracefully."""
        with patch.object(job_search_agent.llm, 'ainvoke', AsyncMock(side_effect=Exception("LLM error"))):
            result = await job_search_agent.analyze_job_fit("Some job description.")

        # Should default to is_fit=True on error
        assert result.is_fit is True
        assert "analysis error" in result.reasoning

    @pytest.mark.asyncio
    async def test_run_job_search_success(self, job_search_agent, mock_browser_session):
        """Test job search returns URLs successfully."""
        # Mock the search agent
        mock_history = MagicMock()
        mock_history.is_successful.return_value = True
        mock_history.final_result.return_value = "https://linkedin.com/jobs/1, https://indeed.com/jobs/2"

        with patch('app.agents.job_search_agent.Agent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value=mock_history)
            mock_agent_class.return_value = mock_agent

            urls = await job_search_agent.run_job_search("Python developer", limit=5)

        assert len(urls) == 2
        assert urls[0] == "https://linkedin.com/jobs/1"
        assert urls[1] == "https://indeed.com/jobs/2"

    @pytest.mark.asyncio
    async def test_run_job_search_no_results(self, job_search_agent):
        """Test job search when no results are found."""
        mock_history = MagicMock()
        mock_history.is_successful.return_value = True
        mock_history.final_result.return_value = ""

        with patch('app.agents.job_search_agent.Agent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value=mock_history)
            mock_agent_class.return_value = mock_agent

            urls = await job_search_agent.run_job_search("Nonexistent job title", limit=5)

        assert urls == []

    @pytest.mark.asyncio
    async def test_run_job_search_failed_search(self, job_search_agent):
        """Test job search when the search fails."""
        mock_history = MagicMock()
        mock_history.is_successful.return_value = False

        with patch('app.agents.job_search_agent.Agent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value=mock_history)
            mock_agent_class.return_value = mock_agent

            urls = await job_search_agent.run_job_search("Python developer", limit=5)

        assert urls == []

    @pytest.mark.asyncio
    async def test_search_and_filter_jobs(self, job_search_agent):
        """Test combined search and filter functionality."""
        # Mock job search to return URLs
        mock_history = MagicMock()
        mock_history.is_successful.return_value = True
        mock_history.final_result.return_value = "https://linkedin.com/jobs/1, https://indeed.com/jobs/2"

        # Mock job fit analysis to return one fit and one not fit
        mock_fit_response = MagicMock()
        mock_fit_response.completion = JobFitAnalysis(is_fit=True, reasoning="Good match")

        mock_not_fit_response = MagicMock()
        mock_not_fit_response.completion = JobFitAnalysis(is_fit=False, reasoning="Not a match")

        with patch('app.agents.job_search_agent.Agent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value=mock_history)
            mock_agent_class.return_value = mock_agent

            # Mock analyze_job_fit for first URL (fit)
            with patch.object(job_search_agent, 'analyze_job_fit', AsyncMock(return_value=mock_fit_response.completion)):
                # For second URL, we need a different mock
                async def mock_analyze_fit(job_desc):
                    if "indeed" in job_desc:
                        return mock_not_fit_response.completion
                    return mock_fit_response.completion

                job_search_agent.analyze_job_fit = mock_analyze_fit

                filtered_jobs = await job_search_agent.search_and_filter_jobs("Python developer", limit=5)

        # Should only return the fitting job
        assert len(filtered_jobs) == 1
        assert filtered_jobs[0]["url"] == "https://linkedin.com/jobs/1"
        assert filtered_jobs[0]["is_fit"] is True
