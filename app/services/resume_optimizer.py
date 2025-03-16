from typing import List, Tuple
from app.models.resume import Resume, JobDescription, OptimizationResponse
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ResumeOptimizer:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
            
        self.llm = ChatOpenAI(
            model_name="gpt-4-turbo-preview",
            temperature=0.7,
            api_key=api_key
        )
        
        self.optimization_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume writer and career coach. Your task is to optimize 
                      a resume to better match a job description while maintaining truthfulness 
                      and professional standards.

                      Format the output following these rules:
                      1. Use clear section headers in ALL CAPS (e.g., EXPERIENCE, EDUCATION)
                      2. Use consistent spacing - one blank line between sections, no double spacing
                      3. Use bullet points (•) for listing achievements and responsibilities
                      4. Align dates to the right for experience and education entries
                      5. Use bold for job titles and company names (wrap in ** for markdown)
                      6. Remove any unnecessary whitespace or tabs
                      7. Ensure consistent indentation for bullet points
                      8. Use proper line breaks to separate different entries
                      9. Format contact information in a clean, professional header
                      10. Use a consistent date format (e.g., MM/YYYY)"""),
            ("user", """Job Description: {job_description}

                    Current Resume Section: {resume_section}

                    Please rewrite this section to better match the job description while maintaining 
                    truthfulness. Focus on relevant skills and experiences. Format the output following 
                    the system instructions. Optimization level: {optimization_level}""")
        ])

        self.formatting_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume formatter. Your task is to ensure the resume is 
                      perfectly formatted for human readability.
                      
                      Follow these formatting rules:
                      1. Use clear section headers in ALL CAPS
                      2. One blank line between sections
                      3. Use bullet points (•) for lists
                      4. Right-align dates
                      5. Bold titles and companies
                      6. Remove extra whitespace and tabs
                      7. Consistent indentation
                      8. Clean line breaks between entries
                      9. Professional header layout
                      10. Consistent date format (MM/YYYY)
                      11. Ensure the output is in proper markdown format
                      12. No trailing whitespace"""),
            ("user", "Please format this resume while preserving all content: {resume_text}")
        ])

    async def optimize_resume(self, resume: Resume, job_description: JobDescription, 
                            optimization_level: float = 0.5) -> OptimizationResponse:
        optimized_sections = []
        changes_made = []
        
        for section in resume.sections:
            optimized_section, changes = await self._optimize_section(
                section.content,
                job_description.description,
                optimization_level
            )
            optimized_sections.append(optimized_section)
            changes_made.extend(changes)
            
        # Join sections and apply final formatting
        raw_optimized_text = "\n\n".join(optimized_sections)
        
        # Apply additional formatting pass
        formatted_text = await self._format_resume(raw_optimized_text)
            
        optimized_resume = Resume(
            sections=[
                section for section in resume.sections
            ],
            raw_text=formatted_text,
            metadata=resume.metadata
        )
        
        match_score = await self._calculate_match_score(
            optimized_resume.raw_text,
            job_description.description
        )
        
        return OptimizationResponse(
            original_resume=resume,
            optimized_resume=optimized_resume,
            changes_made=changes_made,
            match_score=match_score
        )

    async def _format_resume(self, resume_text: str) -> str:
        """Apply final formatting to ensure consistent, clean output."""
        try:
            response = await self.llm.ainvoke(
                self.formatting_prompt.format_messages(
                    resume_text=resume_text
                )
            )
            return response.content.strip()
        except Exception as e:
            logger.error(f"Error during resume formatting: {str(e)}", exc_info=True)
            return resume_text  # Return original text if formatting fails

    async def _optimize_section(self, section_text: str, job_description: str, 
                              optimization_level: float) -> Tuple[str, List[str]]:
        try:
            response = await self.llm.ainvoke(
                self.optimization_prompt.format_messages(
                    job_description=job_description,
                    resume_section=section_text,
                    optimization_level=optimization_level
                )
            )
            return response.content.strip(), ["Section optimized and reformatted"]
        except Exception as e:
            logger.error(f"Error during section optimization: {str(e)}", exc_info=True)
            return section_text, [f"Error during optimization: {str(e)}"]

    async def _calculate_match_score(self, resume_text: str, job_description: str) -> float:
        # This is a placeholder for the actual matching logic
        # In a real implementation, this would use the LLM to calculate a match score
        return 0.75 