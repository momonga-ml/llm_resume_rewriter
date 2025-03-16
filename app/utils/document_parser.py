from typing import List, Dict
from docx import Document
from pypdf import PdfReader
import io
from app.models.resume import ResumeSection, Resume

class DocumentParser:
    @staticmethod
    def parse_pdf(file_content: bytes) -> Resume:
        """
        Parse a PDF file and extract its content into a structured Resume object.
        """
        pdf = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
            
        # This is a basic implementation
        # In a real application, you would want to:
        # 1. Use more sophisticated text extraction
        # 2. Identify section boundaries
        # 3. Extract structured information
        # 4. Handle formatting
        
        return Resume(
            sections=[
                ResumeSection(
                    title="Content",
                    content=text
                )
            ],
            raw_text=text,
            metadata={"file_type": "pdf"}
        )

    @staticmethod
    def parse_docx(file_content: bytes) -> Resume:
        """
        Parse a DOCX file and extract its content into a structured Resume object.
        """
        doc = Document(io.BytesIO(file_content))
        sections: List[Dict] = []
        full_text = []
        
        current_section = {"title": "Header", "content": []}
        
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if not text:
                continue
                
            # Basic section detection
            # In a real implementation, you would want more sophisticated section detection
            if paragraph.style.name.startswith('Heading'):
                if current_section["content"]:
                    sections.append(ResumeSection(
                        title=current_section["title"],
                        content="\n".join(current_section["content"])
                    ))
                current_section = {"title": text, "content": []}
            else:
                current_section["content"].append(text)
                full_text.append(text)
        
        # Add the last section
        if current_section["content"]:
            sections.append(ResumeSection(
                title=current_section["title"],
                content="\n".join(current_section["content"])
            ))
        
        return Resume(
            sections=sections,
            raw_text="\n".join(full_text),
            metadata={"file_type": "docx"}
        ) 