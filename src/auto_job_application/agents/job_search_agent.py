from browser_use import Agent, BrowserSession
from browser_use.llm import ChatOpenAI, UserMessage

from ..config import BROWSER_AGENT_NVIDIA_MODEL, NVIDIA_API_KEY, NVIDIA_BASE_URL
from ..logger_config import get_logger
from ..models.llm_responses import JobFitAnalysis
from .base_agent import BaseAgent
from .knowledge_base_agent import KnowledgeBaseAgent

logger = get_logger(__name__)

class JobSearchAgent(BaseAgent):
    """
    Responsible for searching, analyzing, and filtering applicable job openings.
    Uses browser-use to query job listings and NVIDIA LLM to perform fit analyses
    based on the applicant's profile summary.

    Inherits:
        BaseAgent
    """

    def __init__(self, browser: BrowserSession, knowledge_base: KnowledgeBaseAgent, llm: ChatOpenAI | None = None):
        """
        Initializes the JobSearchAgent with a browser session and knowledge base.

        Args:
            browser (BrowserSession): Active browser-use session for page automation.
            knowledge_base (KnowledgeBaseAgent): Initialized knowledge base agent.
            llm (ChatOpenAI, optional): Pre-initialized model instance.
        """
        self.browser = browser
        self.knowledge_base = knowledge_base
        super().__init__()

        # Setup LLM resources using injected model or fallback
        self.llm = llm or ChatOpenAI(
            model=BROWSER_AGENT_NVIDIA_MODEL,
            base_url=NVIDIA_BASE_URL,
            api_key=NVIDIA_API_KEY,
            reasoning_effort="low",
        )

    async def analyze_job_fit(self, job_description: str) -> JobFitAnalysis:
        """
        Analyzes if a job description fits the applicant based on their knowledge base.

        Args:
            job_description (str): Full text or snippet of the target job description.

        Returns:
            JobFitAnalysis: Pydantic response model containing is_fit (bool) and reasoning (str).
        """
        self.logger.info("Analyzing job fit against applicant profile summary...")

        # Get a summary of the applicant's profile from the knowledge base
        profile_summary = self.knowledge_base.query(
            "Provide a comprehensive summary of the applicant's professional background, skills, and experience."
        )

        prompt = f"""
        You are an expert career advisor. Your task is to determine if a job is a good fit for an applicant.

        Applicant Profile Summary:
        {profile_summary}

        Job Description:
        {job_description}

        Evaluate the fit based on:
        1. Required skills vs applicant's skills.
        2. Experience level required vs applicant's experience.
        3. Core responsibilities vs applicant's background.

        Return your response in the following JSON format:
        {{
            "is_fit": boolean,
            "reasoning": "A brief explanation of why this is or isn't a good fit."
        }}
        """

        try:
            response = await self.llm.ainvoke(
                messages=[UserMessage(content=prompt)],
                output_format=JobFitAnalysis,
            )

            result = response.completion
            self.logger.info(f"Fit analysis result: {result.is_fit} - {result.reasoning}")
            return result
        except Exception as e:
            self.logger.error(f"Error occurred during job fit analysis: {e}")
            # Resilient default: return True to avoid blocking applications on LLM failures
            return JobFitAnalysis(is_fit=True, reasoning="Defaulting to True due to analysis error.")

    async def run_job_search(self, query: str, limit: int = 5) -> list[str]:
        """
        Runs browser automation to search Google/job boards for openings matching a query.

        Args:
            query (str): Job title or search query (e.g., 'Python Developer').
            limit (int, optional): Max number of job URLs to return. Defaults to 5.

        Returns:
            list[str]: Extracted application or job description URLs.
        """
        self.logger.info(f"Initiating browser job search for query: '{query}'")

        search_instructions = f"""
        1. Go to Google and search for "{query} jobs".
        2. Look for job listings on sites like LinkedIn, Indeed, Greenhouse, Lever, or company career pages.
        3. Extract the direct application URLs for at least {limit} relevant job postings.
        4. Return ONLY a comma-separated list of URLs.
        """

        search_agent = Agent(
            task=search_instructions,
            llm=self.llm,
            browser=self.browser,
        )

        history = await search_agent.run()
        result = history.final_result() if history.is_successful() else ""

        if not result:
            self.logger.warning("No job URLs extracted during browser search.")
            return []

        urls = [url.strip() for url in result.split(",") if url.strip().startswith("http")]
        self.logger.info(f"Successfully discovered {len(urls)} job URLs.")
        return urls[:limit]

    async def search_and_filter_jobs(self, query: str, limit: int = 5) -> list[dict]:
        """
        Searches for jobs and filters them based on a personalized fit analysis.

        Args:
            query (str): Job search query (e.g., 'Python Developer').
            limit (int, optional): Maximum number of fitting jobs to return. Defaults to 5.

        Returns:
            list[dict]: List of dictionaries with keys: 'url', 'is_fit', 'reasoning'.
        """
        self.logger.info(f"Searching and filtering jobs for query: '{query}'")

        # Fetch more to allow for filtering
        job_urls = await self.run_job_search(query, limit=limit * 2)

        filtered_jobs = []
        for url in job_urls:
            # Extract job description (actual extraction would scrape; using placeholder)
            job_description = f"Job at {url}"

            fit_analysis = await self.analyze_job_fit(job_description)

            if fit_analysis.is_fit:
                filtered_jobs.append({
                    "url": url,
                    "is_fit": fit_analysis.is_fit,
                    "reasoning": fit_analysis.reasoning
                })

        self.logger.info(f"Retained {len(filtered_jobs)} fitting jobs out of {len(job_urls)} searched.")
        return filtered_jobs[:limit]
