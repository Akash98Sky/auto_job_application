from browser_use import Agent, Browser, Controller
from browser_use.llm import ChatGroq, UserMessage

from .knowledge_base import KnowledgeBase
from .models.llm_responses import JobFitAnalysis
from .resume_manager import ResumeManager
from .logger_config import get_logger
from .config import AGENT_MODEL_NAME, RESUMES_DIR

logger = get_logger(__name__)

class JobApplicationAgent:
    def __init__(self, browser: Browser, model_name=AGENT_MODEL_NAME, temp=0):
        # Setup resources
        self.browser = browser
        self.llm = ChatGroq(model=model_name, temperature=temp)

        # Initialize components
        self.knowledge_base = KnowledgeBase()
        self.knowledge_base.load_from_directory()

        self.resume_manager = ResumeManager(resumes_dir=RESUMES_DIR, llm=self.llm)
        self.resume_manager.load_resumes()

    def _build_controller(self) -> Controller:
        """
        Creates a browser-use Controller and registers the knowledge base
        as a callable tool so the agent can query it on demand.
        """
        controller = Controller()
        kb = self.knowledge_base  # local ref for the closure

        @controller.action(
            "Query the applicant's knowledge base to retrieve facts about their "
            "background, education, employment history, skills, or any other personal "
            "information needed to fill the job application form.",
        )
        def query_knowledge_base(question: str) -> str:
            """
            Args:
                question: A natural-language question about the applicant,
                          e.g. 'What is the applicant's phone number?'
            Returns:
                Relevant facts retrieved from the knowledge base.
            """
            return kb.query(question)

        return controller

    async def analyze_job_fit(self, job_description: str) -> JobFitAnalysis:
        """
        Analyzes if the job is a good fit for the applicant based on their knowledge base.
        Returns a JobFitAnalysis object with 'is_fit' (bool) and 'reasoning' (str).
        """
        logger.info("Analyzing job fit...")
        
        # Get a summary of the applicant's profile from the knowledge base
        profile_summary = self.knowledge_base.query("Provide a comprehensive summary of the applicant's professional background, skills, and experience.")
        
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

    async def apply_to_job(self, job_url: str):
        """
        Navigates to the job URL, uses the ResumeManager to select the best resume,
        and lets the agent query the KnowledgeBase via a tool call when it needs facts.
        """
        logger.info(f"Applying to job at {job_url}")

        # Create an initial agent just to extract the job description
        extract_instructions = f"Go to {job_url} and read the entire page. Extract the core job description, requirements, and responsibilities. Return ONLY this extracted text."
        
        logger.info("Extracting job description from the page...")
        extract_agent = Agent(
            task=extract_instructions,
            llm=self.llm,
            browser=self.browser,
        )
        extract_history = await extract_agent.run()
        
        # Get the final result from the history
        job_description = extract_history.final_result() if extract_history.is_successful() else "General Job Description"
        
        if not job_description:
            job_description = "General Job Description"
            
        logger.info(f"Extracted job description length: {len(job_description)} characters")
    
        # Select the most relevant resume based on extracted description
        best_resume_path = self.resume_manager.get_best_resume(job_description)
        
        if not best_resume_path:
            logger.error("No suitable resume found.")
            return None
            
        logger.info(f"Using resume: {best_resume_path}")

        base_instructions = f"""
You are an autonomous AI applying for a job at {job_url}. The page is already loaded.

If the application requires a resume upload, click the upload button and select
the file at this absolute path: {best_resume_path}.

When you encounter any form field that asks for personal information (name,
contact details, education, work experience, skills, etc.), call the
`query_knowledge_base` tool with a precise question to retrieve the correct
answer before filling the field.

Do not submit the form until all required fields are filled and a resume is attached.
        """

        controller = self._build_controller()

        agent = Agent(
            task=base_instructions,
            llm=self.llm,
            browser=self.browser,
            controller=controller,
            available_file_paths=[best_resume_path]
        )

        history = await agent.run()
        return history

if __name__ == "__main__":
    from dotenv import load_dotenv
    import asyncio
    from .config import BROWSER_EXECUTABLE_PATH, BROWSER_USER_DATA_DIR, BROWSER_PROFILE_DIR
    
    load_dotenv()
    
    # Needs a real browser setup to test
    browser = Browser(
        executable_path=BROWSER_EXECUTABLE_PATH,
        user_data_dir=BROWSER_USER_DATA_DIR,
        profile_directory=BROWSER_PROFILE_DIR,
        wait_between_actions=1000
    )
    
    # We will test using an example url later
    # job_agent = JobApplicationAgent(browser=browser)
    # asyncio.run(job_agent.apply_to_job("https://example.com/job/apply"))
