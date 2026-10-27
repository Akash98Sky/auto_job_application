"""Entry point for the auto-job-application package.

Run with:
    uv run apply
    python -m auto_job_application
"""

import asyncio

from auto_job_application.agents import (
    JobApplicationAgent,
    JobSearchAgent,
    KnowledgeBaseAgent,
    ResumeManagerAgent,
)
from auto_job_application.config import validate_config
from auto_job_application.logger_config import setup_logger
from auto_job_application.session_pool import SessionPool

logger = setup_logger()


async def _async_main():
    logger.info("Verifying configuration...")
    validate_config(raise_on_error=True)
    logger.info("Configuration is valid.")

    session_pool = None
    knowledge_base = None
    resume_manager = None
    search_agent = None
    application_agent = None
    try:
        session_pool = SessionPool()
        browser = await session_pool.get_or_create("main")

        knowledge_base = KnowledgeBaseAgent()
        knowledge_base.load_from_directory()

        resume_manager = ResumeManagerAgent()
        resume_manager.load_resumes()

        # Initialize both agents
        search_agent = JobSearchAgent(browser=browser, knowledge_base=knowledge_base)
        application_agent = JobApplicationAgent(
            browser=browser,
            knowledge_base=knowledge_base,
            resume_manager=resume_manager,
        )

        # Example 1: Search for jobs and get filtered results
        # job_results = await search_agent.search_and_filter_jobs("Python Developer", limit=5)
        # logger.info(f"Found {len(job_results)} fitting jobs:")
        # for job in job_results:
        #     logger.info(f"  - {job['url']}: {job['reasoning']}")

        # Example 2: Apply to a specific job URL
        job_url = "https://www.digicert.com/careers?gh_jid=8505580002&gh_src=my.greenhouse.search"  # Provide target job URL
        logger.info(f"Starting job application on: {job_url}")

        await asyncio.sleep(2)  # Add a delay to allow browser initialization
        history = await application_agent.apply_to_job(job_url)
        return history
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise e
    finally:
        logger.info("Initiating application cleanup and releasing active resources...")
        # Asynchronously close and clean up all agent resources
        if search_agent:
            await search_agent.close()
        if application_agent:
            await application_agent.close()
        if knowledge_base:
            await knowledge_base.close()
        if resume_manager:
            await resume_manager.close()
        if session_pool:
            await session_pool.close_all()
        logger.info("Cleanup completed successfully.")


def main() -> None:
    """Sync entry point for the `apply` console script."""
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
