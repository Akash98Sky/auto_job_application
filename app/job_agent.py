from browser_use import Agent, Browser, Controller
from browser_use.llm import ChatGroq

from .knowledge_base import KnowledgeBase
from .resume_manager import ResumeManager

class JobApplicationAgent:
    def __init__(self, browser: Browser, model_name="openai/gpt-oss-120b", temp=0):
        # Setup resources
        self.browser = browser
        self.llm = ChatGroq(model=model_name, temperature=temp)

        # Initialize components
        self.knowledge_base = KnowledgeBase()
        self.knowledge_base.load_from_directory()

        self.resume_manager = ResumeManager(llm=self.llm)
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

    async def apply_to_job(self, job_url: str):
        """
        Navigates to the job URL, uses the ResumeManager to select the best resume,
        and lets the agent query the KnowledgeBase via a tool call when it needs facts.
        """
        print(f"Applying to job at {job_url}")

        # Select the most relevant resume (simple fallback for now)
        best_resume_path = self.resume_manager.get_best_resume("General Job Description")
        print(f"Using resume: {best_resume_path}")

        base_instructions = f"""
You are an autonomous AI applying for a job at {job_url}.

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
    
    load_dotenv()
    
    # Needs a real browser setup to test
    browser = Browser(
        executable_path='C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
        user_data_dir='./profile',
        profile_directory='Default',
        wait_between_actions=1000
    )
    
    # We will test using an example url later
    # job_agent = JobApplicationAgent(browser=browser)
    # asyncio.run(job_agent.apply_to_job("https://example.com/job/apply"))
