import asyncio
from browser_use import Agent, BrowserSession, Tools
from browser_use.llm import ChatOpenAI

from .base_agent import BaseAgent
from .knowledge_base_agent import KnowledgeBaseAgent
from .resume_manager_agent import ResumeManagerAgent
from ..logger_config import get_logger
from ..config import BROWSER_AGENT_NVIDIA_MODEL, NVIDIA_API_KEY, NVIDIA_BASE_URL

logger = get_logger(__name__)

class JobApplicationAgent(BaseAgent):
    """
    Responsible for applying to jobs automatically.
    Handles job description extraction, resume selection via ResumeManager,
    and automatic form filling by querying applicant memory via a registered custom tool.

    Inherits:
        BaseAgent
    """

    def __init__(self, browser: BrowserSession, knowledge_base: KnowledgeBaseAgent, resume_manager: ResumeManagerAgent, llm: ChatOpenAI | None = None):
        """
        Initializes the JobApplicationAgent with browser session and sub-agents.

        Args:
            browser (BrowserSession): Active browser-use session for page automation.
            knowledge_base (KnowledgeBaseAgent): Initialized knowledge base agent.
            resume_manager (ResumeManagerAgent): Initialized resume manager agent.
            llm (ChatOpenAI, optional): Pre-initialized model instance.
        """
        self.browser = browser
        self.knowledge_base = knowledge_base
        self.resume_manager = resume_manager
        super().__init__()

        # Setup LLM resources using injected model or fallback
        self.llm = llm or ChatOpenAI(
            model=BROWSER_AGENT_NVIDIA_MODEL,
            base_url=NVIDIA_BASE_URL,
            api_key=NVIDIA_API_KEY,
            reasoning_effort="low",
        )

    def _build_tools(self) -> Tools:
        """
        Creates a browser-use Tools configuration and registers the knowledge base
        as a callable tool so that the browser agent can query it on demand.

        Returns:
            Tools: Browser-use Tools object with query_knowledge_base registered.
        """
        tools = Tools()
        kb = self.knowledge_base  # local reference for the closure

        @tools.action(
            "Query the applicant's knowledge base to retrieve facts about their "
            "background, education, employment history, skills, or any other personal "
            "information needed to fill the job application form.",
        )
        def query_knowledge_base(question: str) -> str:
            """
            Queries the knowledge base for specific information.

            Args:
                question (str): A natural-language question about the applicant,
                    e.g. 'What is the applicant's phone number?'

            Returns:
                str: Relevant facts retrieved from the knowledge base.
            """
            return kb.query(question)

        return tools

    async def apply_to_job(self, job_url: str) -> Agent | None:
        """
        Navigates to the job URL, extracts the description, uses the ResumeManager to select
        the best-matching resume, and runs browser-use Agent to complete the application.

        Args:
            job_url (str): Absolute URL of the target job application form.

        Returns:
            Agent history or completion logs, or None if no resume is found.
        """
        self.logger.info(f"Initiating job application at URL: {job_url}")

        # Create an initial agent just to extract the job description
        extract_instructions = (
            f"Go to {job_url} and read the entire page. Extract the core job description, "
            "requirements, and responsibilities. Return ONLY this extracted text."
        )

        self.logger.info("Extracting job description from page...")

        extractor_agent = Agent(
            task=extract_instructions,
            llm=self.llm,
            browser=self.browser
        )
        
        try:
            extract_history = await extractor_agent.run(max_steps=5)
            job_description = extract_history.final_result() if extract_history.is_successful() else "General Job Description"
        except Exception as e:
            self.logger.error(f"Failed to extract job description: {e}")
            job_description = "General Job Description"
        finally:
            await extractor_agent.close()

        if not job_description:
            job_description = "General Job Description"

        self.logger.info(f"Extracted job description length: {len(job_description)} characters")

        # Select the most relevant resume based on extracted description
        best_resume_path = await self.resume_manager.get_best_resume(job_description)

        if not best_resume_path:
            self.logger.error("No suitable resume found; aborting application process.")
            return None

        self.logger.info(f"Using matched resume PDF path: {best_resume_path}")
        await asyncio.sleep(2)  # Allow browser session to reset

        base_instructions = f"""
        You are an autonomous AI applying for jobs.

        Job URL: {job_url}
        At first, check the current URL is the job application URL. If not, navigate to the application form.

        If the application requires a resume upload, click the upload button and select
        the file at this absolute path: {best_resume_path}.

        When you encounter any form field that asks for personal information (name,
        contact details, education, work experience, skills, etc.), always use the
        `query_knowledge_base` action with a precise question to retrieve the correct
        answer before filling the field.

        Do not submit the form until all required fields are filled and a resume is attached.
        """

        application_agent = Agent(
            task=base_instructions,
            llm=self.llm,
            tools=self._build_tools(),
            available_file_paths=[best_resume_path],
            browser=self.browser,
            use_vision=True,
            directly_open_url=False
        )

        try:
            history = await application_agent.run(max_steps=20)
            return history
        finally:
            await application_agent.close()
