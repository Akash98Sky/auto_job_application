from pydantic import BaseModel, Field

class JobFitAnalysis(BaseModel):
    is_fit: bool = Field(description="Whether the job is a good fit for the applicant")
    reasoning: str = Field(description="A brief explanation of why this is or isn't a good fit")
