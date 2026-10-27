from pathlib import Path

from browser_use.llm import BaseChatModel, ChatGroq, UserMessage
from langchain_core.prompts import PromptTemplate
from pypdf import PdfReader

from ..config import RESUME_AGENT_GROQ_MODEL, RESUMES_DIR
from ..logger_config import get_logger
from .base_agent import BaseAgent

logger = get_logger(__name__)


class ResumeManagerAgent(BaseAgent):
    """
    Manages loading, parsing, and ranking applicant resumes against a job description.
    Uses PyPDF for PDF parsing and Groq LLM for resume matching and ranking.

    Inherits:
        BaseAgent
    """

    def __init__(self, resumes_dir: str = RESUMES_DIR, llm: BaseChatModel | None = None):
        """
        Initializes the ResumeManagerAgent with a specified resumes directory and LLM client.

        Args:
            resumes_dir (str): Path to the directory containing resume PDF files.
            llm (BaseChatModel, optional): An optional pre-initialized ChatModel instance.
        """
        self.resumes_dir = Path(resumes_dir)
        self.resumes_dir.mkdir(parents=True, exist_ok=True)
        self.resumes: dict[str, str] = {}  # Dictionary mapping file path to extracted text
        super().__init__()

        # Initialize an LLM for ranking, or use the one provided
        self.llm = llm or ChatGroq(model=RESUME_AGENT_GROQ_MODEL, temperature=0)

    def load_resumes(self) -> None:
        """
        Scans the resumes directory and extracts text from all PDF files.
        Populates self.resumes with absolute paths mapped to extracted text content.
        """
        self.logger.info(f"Loading resumes from {self.resumes_dir}...")
        for pdf_path in self.resumes_dir.glob("*.pdf"):
            try:
                reader = PdfReader(pdf_path)
                text = ""
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                self.resumes[str(pdf_path)] = text
                self.logger.info(f"Successfully loaded resume: {pdf_path.name}")
            except Exception as e:
                self.logger.error(f"Failed to load resume {pdf_path.name}: {e}")

    @property
    def data_dir(self) -> Path:
        """
        Returns the path to the resumes directory.

        Returns:
            Path: Path to the resumes directory.
        """
        return self.resumes_dir

    async def get_best_resume(self, job_description: str) -> str:
        """
        Ranks all loaded resumes against the given job description using an LLM.
        Returns the absolute file path to the best-matching resume PDF.

        Args:
            job_description (str): Text of the target job description to match against.

        Returns:
            str: Absolute path to the best-matching resume PDF file.

        Raises:
            ValueError: If no resumes have been loaded prior to calling.
        """
        if not self.resumes:
            raise ValueError("No resumes loaded. Please load resumes before calling this method.")

        if len(self.resumes) == 1:
            best_resume = next(iter(self.resumes.keys()))
            self.logger.info(f"Only one resume found: {Path(best_resume).name}")
            return str(Path(best_resume).absolute())

        # Rank resumes against job description using LLM
        prompt_template = PromptTemplate(
            input_variables=["resumes_text", "job_description"],
            template="""You are an expert technical recruiter analyzing resumes against a job description.
Your goal is to choose the BEST resume ID for the job.

Job Description:
{job_description}

Available Resumes:
{resumes_text}

Output ONLY the "Resume ID" value of the best matching resume, nothing else. No explanation.""",
        )

        resumes_text = ""
        for i, (path, text) in enumerate(self.resumes.items()):
            resumes_text += f"Resume ID: {i}\nFile: {path}\nContent:\n{text[:2000]}\n\n"  # truncating content for context length

        try:
            prompt = prompt_template.format(
                resumes_text=resumes_text, job_description=job_description[:2000]
            )  # truncating job description
            result = await self.llm.ainvoke(messages=[UserMessage(content=prompt)])

            selected_id_str = str(result.completion).strip()
            self.logger.info(f"LLM Selected Resume ID: {selected_id_str}")

            try:
                selected_id = int(selected_id_str)
                selected_path = list(self.resumes.keys())[selected_id]
                return str(Path(selected_path).absolute())
            except (ValueError, IndexError):
                self.logger.warning(
                    f"Could not parse or resolve selected ID: {selected_id_str}. Falling back to default."
                )
                return str(Path(next(iter(self.resumes.keys()))).absolute())
        except Exception as e:
            self.logger.error(f"Error ranking resumes: {e}")
            return str(Path(next(iter(self.resumes.keys()))).absolute())


if __name__ == "__main__":
    import asyncio

    from dotenv import load_dotenv

    load_dotenv()

    async def run_test():
        rm = ResumeManagerAgent()
        rm.load_resumes()
        if rm.resumes:
            best_resume_path = await rm.get_best_resume(
                "Need a Python Django Developer with AWS experience"
            )
            logger.info(f"Best resume selected: {best_resume_path}")
        else:
            logger.warning("No resumes loaded. Place PDFs in resumes directory to test.")

    asyncio.run(run_test())
