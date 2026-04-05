import asyncio
from browser_use import Agent, BrowserSession, Controller, Tools
from browser_use.llm import ChatOpenAI

from .knowledge_base_agent import KnowledgeBaseAgent
from .resume_manager_agent import ResumeManagerAgent
from ..logger_config import get_logger
from ..config import BROWSER_AGENT_NVIDIA_MODEL, NVIDIA_API_KEY, NVIDIA_BASE_URL

logger = get_logger(__name__)


class JobApplicationAgent:
    """
    Responsible for applying to jobs. Handles job description extraction,
    resume selection, and form filling using the knowledge base.
    """

    def __init__(self, browser: BrowserSession, knowledge_base: KnowledgeBaseAgent, resume_manager: ResumeManagerAgent):
        # Setup LLM resources
        self.browser = browser
        self.llm = ChatOpenAI(
            model=BROWSER_AGENT_NVIDIA_MODEL,
            base_url=NVIDIA_BASE_URL,
            api_key=NVIDIA_API_KEY,
            reasoning_effort="low",
        )

        # Initialize sub-agents for knowledge base and resume management
        self.knowledge_base = knowledge_base
        self.resume_manager = resume_manager

    def _build_tools(self) -> Tools:
        """
        Creates a browser-use Tools and registers the knowledge base
        as a callable tool so the agent can query it on demand.
        """
        tools = Tools()
        kb = self.knowledge_base  # local ref for the closure

        @tools.action(
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

        return tools

    async def apply_to_job(self, job_url: str):
        """
        Navigates to the job URL, uses the ResumeManager to select the best resume,
        and lets the agent query the KnowledgeBase via a tool call when it needs facts.
        """
        logger.info(f"Applying to job at {job_url}")

        # Create an initial agent just to extract the job description
        extract_instructions = (
            f"Go to {job_url} and read the entire page. Extract the core job description, "
            "requirements, and responsibilities. Return ONLY this extracted text."
        )

        logger.info("Extracting job description from the page...")

        extractor_agent = Agent(
            task=extract_instructions,
            llm=self.llm,
            browser=self.browser
        )
        extract_history = await extractor_agent.run(max_steps=5)

        # Get the final result from the history
        job_description = extract_history.final_result() if extract_history.is_successful() else "General Job Description"

        if not job_description:
            job_description = "General Job Description"

        logger.info(f"Extracted job description length: {len(job_description)} characters")

        # Select the most relevant resume based on extracted description
        best_resume_path = await self.resume_manager.get_best_resume(job_description)

        if not best_resume_path:
            logger.error("No suitable resume found.")
            await extractor_agent.close()
            return None

        logger.info(f"Using resume: {best_resume_path}")

        await extractor_agent.close()  # Close the extractor agent before starting the application agent
        await asyncio.sleep(2)  # Add a delay to allow browser reset

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

        history = await application_agent.run(max_steps=20)
        await application_agent.close()

        return history
