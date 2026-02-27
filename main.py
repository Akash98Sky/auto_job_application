import asyncio
from dotenv import load_dotenv
from logger_config import setup_logger

logger = setup_logger()

# Ensure browser_use is installed and imported correctly
try:
    from browser_use import Browser
except ImportError:
    print("browser-use package not found. Please make sure to install dependencies.")
    import sys
    sys.exit(1)

from job_agent import JobApplicationAgent

load_dotenv()

async def main():
    browser = Browser(
        executable_path='C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
        user_data_dir='./profile',
        profile_directory='Default',
        wait_between_actions=1000,
        args=['--disable-extensions']
    )

    try:
        agent = JobApplicationAgent(
            browser=browser,
            model_name='meta-llama/llama-4-scout-17b-16e-instruct'  # Or use what was previously set for meta-llama
        )
        
        job_url = "https://www.netskope.com/company/careers/open-positions?gh_jid=7601631&gh_src=my.greenhouse.search" # Provide target job URL
        print(f"Starting job application on: {job_url}")
        
        await asyncio.sleep(5)  # Add a delay to allow browser initialization
        history = await agent.apply_to_job(job_url)
        return history
    except Exception as e:
        print(f"Error occurred: {e}")
        raise e
    finally:
        if browser:
            await browser.stop()

if __name__ == "__main__":
    history = asyncio.run(main())

