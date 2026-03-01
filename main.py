import asyncio
from browser_use import Browser

from app.job_agent import JobApplicationAgent
from app.logger_config import setup_logger
from app.config import BROWSER_EXECUTABLE_PATH, BROWSER_USER_DATA_DIR, BROWSER_PROFILE_DIR, AGENT_MODEL_NAME

logger = setup_logger()

async def main():
    browser = Browser(
        executable_path=BROWSER_EXECUTABLE_PATH,
        user_data_dir=BROWSER_USER_DATA_DIR,
        profile_directory=BROWSER_PROFILE_DIR,
        wait_between_actions=1000,
        args=['--disable-extensions']
    )

    try:
        agent = JobApplicationAgent(
            browser=browser,
            model_name=AGENT_MODEL_NAME
        )
        
        job_url = "https://www.netskope.com/company/careers/open-positions?gh_jid=7601631&gh_src=my.greenhouse.search" # Provide target job URL
        logger.info(f"Starting job application on: {job_url}")
        
        await asyncio.sleep(5)  # Add a delay to allow browser initialization
        history = await agent.apply_to_job(job_url)
        return history
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise e
    finally:
        if browser:
            await browser.stop()

if __name__ == "__main__":
    history = asyncio.run(main())

