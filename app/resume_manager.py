from pathlib import Path
from langchain_core.language_models import BaseChatModel
from pypdf import PdfReader
from langchain_core.prompts import PromptTemplate
from .logger_config import get_logger
from .config import RESUMES_DIR, RESUME_MODEL_NAME

logger = get_logger(__name__)

class ResumeManager:
    def __init__(self, resumes_dir: str = RESUMES_DIR, llm: BaseChatModel | None = None):
        self.resumes_dir = Path(resumes_dir)
        self.resumes_dir.mkdir(parents=True, exist_ok=True)
        self.resumes = {}  # Make a dictionary mapping path to extracted text
        # Initialize an LLM for ranking, or use the one provided
        self.llm = llm or ChatGroq(model=RESUME_MODEL_NAME, temperature=0)

    def load_resumes(self):
        """Scans the resumes directory and extracts text from all PDF files."""
        logger.info(f"Loading resumes from {self.resumes_dir}...")
        for pdf_path in self.data_dir.glob("*.pdf"):
            try:
                reader = PdfReader(pdf_path)
                text = ""
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                self.resumes[str(pdf_path)] = text
                logger.info(f"Loaded resume: {pdf_path.name}")
            except Exception as e:
                logger.error(f"Failed to load resume {pdf_path.name}: {e}")

    @property
    def data_dir(self):
        return self.resumes_dir

    def get_best_resume(self, job_description: str) -> str:
        """
        Ranks the loaded resumes against a job description using an LLM.
        Returns the absolute file path to the best-matching resume PDF.
        """
        if not self.resumes:
            raise ValueError("No resumes loaded. Please load resumes before calling this method.")
        
        if len(self.resumes) == 1:
            best_resume = list(self.resumes.keys())[0]
            logger.info(f"Only one resume found: {Path(best_resume).name}")
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

Output ONLY the "Resume ID" value of the best matching resume, nothing else. No explanation."""
        )

        resumes_text = ""
        for i, (path, text) in enumerate(self.resumes.items()):
            resumes_text += f"Resume ID: {i}\nFile: {path}\nContent:\n{text[:2000]}\n\n" # truncating content for context length
            
        try:
            chain = prompt_template | self.llm
            result = chain.invoke({
                "job_description": job_description[:2000],
                "resumes_text": resumes_text
            })
            
            selected_id_str = str(result.content).strip()
            logger.info(f"LLM Selected Resume ID: {selected_id_str}")
            
            try:
                selected_id = int(selected_id_str)
                selected_path = list(self.resumes.keys())[selected_id]
                return str(Path(selected_path).absolute())
            except ValueError:
                 logger.warning(f"Could not parse selected ID: {selected_id_str}. Falling back to default.")
                 return str(Path(list(self.resumes.keys())[0]).absolute())
        except Exception as e:
             logger.error(f"Error ranking resumes: {e}")
             return str(Path(list(self.resumes.keys())[0]).absolute())


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    rm = ResumeManager()
    rm.load_resumes()
    
    # Needs a sample resume to actually test, but this initializes successfully
    best_resume_path = rm.get_best_resume("Need a Python Django Developer with AWS experience")
    logger.info(f"Best resume selected: {best_resume_path}")
