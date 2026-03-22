from browser_use import Agent, BrowserSession
from browser_use.llm import ChatOpenAI, UserMessage

from .knowledge_base_agent import KnowledgeBaseAgent
from ..models.llm_responses import JobFitAnalysis
from ..logger_config import get_logger
from ..config import BROWSER_AGENT_NVIDIA_MODEL, NVIDIA_API_KEY, NVIDIA_BASE_URL

logger = get_logger(__name__)


class JobSearchAgent:
    """
    Responsible for searching, analyzing, and filtering applicable job openings.
    """

    def __init__(self, browser: BrowserSession, knowledge_base: KnowledgeBaseAgent):
        # Setup LLM resources
        self.browser = browser
        self.llm = ChatOpenAI(
            model=BROWSER_AGENT_NVIDIA_MODEL,
            base_url=NVIDIA_BASE_URL,
            api_key=NVIDIA_API_KEY,
            reasoning_effort="low",
        )

        # Initialize knowledge base for job fit analysis
        self.knowledge_base = knowledge_base

    async def analyze_job_fit(self, job_description: str) -> JobFitAnalysis:
        """
        Analyzes if the job is a good fit for the applicant based on their knowledge base.
        Returns a JobFitAnalysis object with 'is_fit' (bool) and 'reasoning' (str).
        """
        logger.info("Analyzing job fit...")

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
            logger.info(f"Fit analysis result: {result.is_fit} - {result.reasoning}")
            return result
        except Exception as e:
            logger.error(f"Error analyzing job fit: {e}")
            return JobFitAnalysis(is_fit=True, reasoning="Defaulting to True due to analysis error.")

    async def run_job_search(self, query: str, limit: int = 5) -> list[str]:
        """
        Uses browser-use to search for jobs based on a query and returns a list of job URLs.
        """
        logger.info(f"Searching for jobs with query: {query}")

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
            logger.warning("No job URLs found during search.")
            return []

        urls = [url.strip() for url in result.split(",") if url.strip().startswith("http")]
        logger.info(f"Found {len(urls)} job URLs.")
        return urls[:limit]

    async def search_and_filter_jobs(self, query: str, limit: int = 5) -> list[dict]:
        """
        Searches for jobs and filters them based on job fit analysis.
        Returns a list of dictionaries containing job URLs and fit analysis.
        """
        logger.info(f"Searching and filtering jobs for query: {query}")

        job_urls = await self.run_job_search(query, limit=limit * 2)  # Get more to filter

        filtered_jobs = []
        for url in job_urls:
            # Extract job description from URL (simplified - in practice, you'd scrape the page)
            job_description = f"Job at {url}"  # Placeholder - actual extraction would require browser agent

            fit_analysis = await self.analyze_job_fit(job_description)

            if fit_analysis.is_fit:
                filtered_jobs.append({
                    "url": url,
                    "is_fit": fit_analysis.is_fit,
                    "reasoning": fit_analysis.reasoning
                })

        logger.info(f"Found {len(filtered_jobs)} fitting jobs out of {len(job_urls)} searched.")
        return filtered_jobs
