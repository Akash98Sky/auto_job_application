import asyncio

from app.agents import JobSearchAgent, JobApplicationAgent, KnowledgeBaseAgent, ResumeManagerAgent
from app.logger_config import setup_logger
from app.session_pool import SessionPool

logger = setup_logger()


async def main():
    try:
        session_pool = SessionPool()
        browser = await session_pool.get_or_create("main")

        knowledge_base = KnowledgeBaseAgent()
        knowledge_base.load_from_directory()

        resume_manager = ResumeManagerAgent()
        resume_manager.load_resumes()

        # Initialize both agents
        search_agent = JobSearchAgent(browser=browser, knowledge_base=knowledge_base)
        application_agent = JobApplicationAgent(browser=browser, knowledge_base=knowledge_base, resume_manager=resume_manager)

        # Example 1: Search for jobs and get filtered results
        # job_results = await search_agent.search_and_filter_jobs("Python Developer", limit=5)
        # logger.info(f"Found {len(job_results)} fitting jobs:")
        # for job in job_results:
        #     logger.info(f"  - {job['url']}: {job['reasoning']}")

        # Example 2: Apply to a specific job URL
        job_url = "https://job-boards.greenhouse.io/bugcrowd/jobs/7507933?gh_jid=7507933&gh_src=my.greenhouse.search"  # Provide target job URL
        logger.info(f"Starting job application on: {job_url}")

        await asyncio.sleep(2)  # Add a delay to allow browser initialization
        history = await application_agent.apply_to_job(job_url)
        return history
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise e


if __name__ == "__main__":
    history = asyncio.run(main())
