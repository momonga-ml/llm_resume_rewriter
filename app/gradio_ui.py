import gradio as gr
from app.utils.document_parser import DocumentParser
from app.services.resume_optimizer import ResumeOptimizer
from app.models.resume import JobDescription
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the resume optimizer
resume_optimizer = ResumeOptimizer()

async def process_resume(
    resume_file,
    job_title: str,
    job_description: str,
    company_name: str,
    optimization_level: float
) -> tuple[str, str, float]:
    """
    Process the resume and return the optimized version
    """
    try:
        # Debug logging for inputs
        logger.info("Received inputs for resume processing:")
        logger.info(f"Resume file: {type(resume_file)} - {resume_file}")
        logger.info(f"Job title: {type(job_title)} - {job_title}")
        logger.info(f"Job description: {type(job_description)} - {job_description}")
        logger.info(f"Company name: {type(company_name)} - {company_name}")
        logger.info(f"Optimization level: {type(optimization_level)} - {optimization_level}")
        
        # Check if file was uploaded
        if not resume_file:
            logger.warning("No resume file uploaded")
            return "Error: Please upload a file.", "", 0.0
            
        # Debug logging
        logger.debug(f"File type: {type(resume_file)}")
        logger.debug(f"File attributes: {dir(resume_file)}")
            
        # Get the file content as bytes
        try:
            # Handle Gradio's NamedString type (which contains a file path)
            if str(type(resume_file).__name__) == 'NamedString':
                file_name = resume_file.name
                logger.debug(f"Processing NamedString file: {file_name}")
                # Read the actual file from the path
                with open(str(resume_file), 'rb') as f:
                    file_content = f.read()
            # Handle Gradio file upload (new format)
            elif hasattr(resume_file, 'name') and hasattr(resume_file, 'orig_name'):
                file_name = resume_file.orig_name  # Use the original filename
                logger.debug(f"Processing Gradio uploaded file: {file_name}")
                file_content = resume_file.read()
            # Handle file-like objects (for testing)
            elif hasattr(resume_file, 'read'):
                file_content = resume_file.read()
                file_name = getattr(resume_file, 'name', '')
                logger.debug(f"Processing file-like object: {file_name}")
            else:
                error_msg = f"Error: Invalid file format. Got type {type(resume_file)}"
                logger.error(error_msg)
                return error_msg, "", 0.0
        except Exception as e:
            error_msg = f"Error: Could not read file content: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg, "", 0.0
        
        # Determine file type and parse accordingly
        if not file_name:
            logger.error("Could not determine file type - no filename available")
            return "Error: Could not determine file type.", "", 0.0
            
        if file_name.lower().endswith('.pdf'):
            logger.info(f"Parsing PDF file: {file_name}")
            resume = DocumentParser.parse_pdf(file_content)
        elif file_name.lower().endswith('.docx'):
            logger.info(f"Parsing DOCX file: {file_name}")
            resume = DocumentParser.parse_docx(file_content)
        else:
            error_msg = "Error: Unsupported file format. Please upload a PDF or DOCX file."
            logger.error(f"{error_msg} Got filename: {file_name}")
            return error_msg, "", 0.0
            
        # Create job description object
        job_desc = JobDescription(
            title=job_title,
            description=job_description,
            company=company_name
        )
        
        logger.info("Starting resume optimization")
        # Optimize the resume
        result = await resume_optimizer.optimize_resume(
            resume=resume,
            job_description=job_desc,
            optimization_level=optimization_level
        )
        
        # Format the changes made for display
        changes_summary = "\n".join([f"• {change}" for change in result.changes_made])
        logger.info(f"Resume optimization completed. Match score: {result.match_score}")
        
        return (
            result.optimized_resume.raw_text,
            changes_summary,
            result.match_score
        )
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg, "", 0.0

# Create the Gradio interface
def create_ui():
    with gr.Blocks(title="Resume Rewriter LLM", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # Resume Rewriter LLM
        Upload your resume and provide job details to get an optimized version that better matches the position.
        """)
        
        with gr.Row():
            with gr.Column():
                # Input components
                resume_file = gr.File(
                    label="Upload Resume (PDF or DOCX)",
                    file_types=[".pdf", ".docx"]
                )
                job_title = gr.Textbox(
                    label="Job Title",
                    placeholder="e.g., Senior Software Engineer"
                )
                company = gr.Textbox(
                    label="Company Name (Optional)",
                    placeholder="e.g., Tech Corp"
                )
                job_description = gr.Textbox(
                    label="Job Description",
                    placeholder="Paste the full job description here...",
                    lines=5
                )
                optimization_level = gr.Slider(
                    label="Optimization Level",
                    minimum=0.1,
                    maximum=1.0,
                    value=0.5,
                    step=0.1,
                    info="Higher values mean more aggressive changes"
                )
                submit_btn = gr.Button("Optimize Resume", variant="primary")

            with gr.Column():
                # Output components
                optimized_text = gr.Textbox(
                    label="Optimized Resume",
                    lines=10,
                    show_copy_button=True
                )
                changes = gr.Textbox(
                    label="Changes Made",
                    lines=5
                )
                match_score = gr.Number(
                    label="Match Score",
                    info="Score between 0 and 1, higher is better"
                )

        # Handle submission
        submit_btn.click(
            fn=process_resume,
            inputs=[
                resume_file,
                job_title,
                job_description,
                company,
                optimization_level
            ],
            outputs=[
                optimized_text,
                changes,
                match_score
            ],
            api_name="process_resume"  # Add explicit API name
        )

        # Add debug information
        gr.Markdown("""
        ### Debug Information
        If you encounter issues, please check that all fields are filled out correctly:
        - Resume file (PDF or DOCX)
        - Job Title
        - Job Description
        - Company Name
        - Optimization Level
        """)

        gr.Markdown("""
        ### Tips
        - Upload your resume in PDF or DOCX format
        - Provide as much detail as possible in the job description
        - Adjust the optimization level based on how much you want to modify the resume
        """)

    return interface

if __name__ == "__main__":
    ui = create_ui()
    ui.launch() 