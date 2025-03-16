from pydantic import BaseModel
from typing import List, Optional

class ResumeSection(BaseModel):
    title: str
    content: str

class Resume(BaseModel):
    sections: List[ResumeSection]
    raw_text: str
    metadata: Optional[dict] = None

class JobDescription(BaseModel):
    title: str
    description: str
    company: Optional[str] = None
    requirements: Optional[List[str]] = None

class OptimizationRequest(BaseModel):
    resume: Resume
    job_description: JobDescription
    optimization_level: Optional[float] = 0.5  # 0.0 to 1.0, how aggressive the changes should be

class OptimizationResponse(BaseModel):
    original_resume: Resume
    optimized_resume: Resume
    changes_made: List[str]
    match_score: float  # 0.0 to 1.0, how well the resume matches the job description 