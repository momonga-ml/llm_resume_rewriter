import pytest
from pathlib import Path
from app.gradio_ui import process_resume


# mark test as special to run since it uses llm
@pytest.mark.llm
@pytest.mark.asyncio
async def test_process_real_pdf():
    """Integration test using the actual PDF file from docs folder"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    pdf_path = project_root / "docs" / "Charles Frenzel MSFT Resume.pdf"
    
    # Skip test if file doesn't exist
    if not pdf_path.exists():
        pytest.skip(f"Test PDF file not found at {pdf_path}. Please add a test PDF file to the docs directory.")
    
    # Read the PDF file
    with open(pdf_path, 'rb') as f:
        class FileWrapper:
            def __init__(self, content, name):
                self.content = content
                self.name = name
                self.orig_name = name  # Add this for Gradio compatibility
            
            def read(self):
                return self.content
        
        content = f.read()
        file_wrapper = FileWrapper(content, pdf_path.name)
    
    # Test the process_resume function with real data
    result = await process_resume(
        file_wrapper,
        "Software Engineer",
        "Looking for a Python developer with experience in machine learning and web development.",
        "Tech Corp",
        0.5
    )
    
    # Basic validation
    assert isinstance(result, tuple)
    assert len(result) == 3
    assert isinstance(result[0], str)  # optimized text
    assert len(result[0]) > 0  # should have some content
    assert isinstance(result[1], str)  # changes
    assert isinstance(result[2], float)  # match score
    assert 0 <= result[2] <= 1  # score should be between 0 and 1