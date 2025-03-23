import pytest
from app.gradio_ui import process_resume
from app.models.resume import Resume, ResumeSection
from unittest.mock import MagicMock, patch

# Create test fixtures
@pytest.fixture
def sample_pdf_content():
    return b"%PDF-1.4\nSample PDF content"

@pytest.fixture
def sample_docx_content():
    return b"Sample DOCX content"

@pytest.fixture
def mock_file():
    class MockFile:
        def __init__(self, content, name):
            self.content = content
            self.name = name
            self._file = MagicMock()
            self._file.read.return_value = content

        def read(self):
            return self.content

    return MockFile

@pytest.fixture
def mock_resume_optimizer():
    class MockResumeOptimizer:
        async def optimize_resume(self, resume, job_description, optimization_level):
            # Create a mock optimization response
            return type('OptimizationResponse', (), {
                'optimized_resume': Resume(
                    sections=[ResumeSection(title="Test", content="Optimized content")],
                    raw_text="Optimized content",
                    metadata={}
                ),
                'changes_made': ["Changed something"],
                'match_score': 0.8
            })
    return MockResumeOptimizer()

@pytest.fixture
def mock_document_parser():
    class MockDocumentParser:
        @staticmethod
        def parse_pdf(file_content):
            return Resume(
                sections=[ResumeSection(title="Test", content="PDF content")],
                raw_text="PDF content",
                metadata={"file_type": "pdf"}
            )

        @staticmethod
        def parse_docx(file_content):
            return Resume(
                sections=[ResumeSection(title="Test", content="DOCX content")],
                raw_text="DOCX content",
                metadata={"file_type": "docx"}
            )
    return MockDocumentParser

@pytest.fixture
def mock_gradio_file():
    class MockGradioFile:
        def __init__(self, content, orig_name):
            self.name = "temporary_name"  # Gradio's temporary name
            self.orig_name = orig_name    # Original filename
            self._content = content

        def read(self):
            return self._content

    return MockGradioFile

@pytest.fixture
def mock_gradio_named_string(tmp_path):
    # Create a temporary file with sample content
    def create_named_string(content, name):
        # Create a temporary file with the content
        temp_file = tmp_path / name
        temp_file.write_bytes(content)
        
        # Create the NamedString that points to the file
        class MockNamedString(str):
            def __new__(cls, file_path, name):
                instance = super().__new__(cls, str(file_path))
                instance.name = name
                instance.__class__.__name__ = 'NamedString'
                return instance
        
        return MockNamedString(str(temp_file), name)
    
    return create_named_string

@pytest.mark.asyncio
async def test_process_resume_pdf(mock_file, sample_pdf_content, mock_resume_optimizer, mock_document_parser):
    with patch('app.gradio_ui.resume_optimizer', mock_resume_optimizer), \
         patch('app.gradio_ui.DocumentParser', mock_document_parser):
        # Create a mock PDF file
        pdf_file = mock_file(sample_pdf_content, "test.pdf")
        
        # Test the process_resume function
        result = await process_resume(
            pdf_file,
            "Software Engineer",
            "Python developer needed",
            "Test Corp",
            0.5
        )
        
        # Check the results
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], str)  # optimized text
        assert isinstance(result[1], str)  # changes
        assert isinstance(result[2], float)  # match score
        assert result[2] == 0.8  # match score from mock

@pytest.mark.asyncio
async def test_process_resume_docx(mock_file, sample_docx_content, mock_resume_optimizer, mock_document_parser):
    with patch('app.gradio_ui.resume_optimizer', mock_resume_optimizer), \
         patch('app.gradio_ui.DocumentParser', mock_document_parser):
        # Create a mock DOCX file
        docx_file = mock_file(sample_docx_content, "test.docx")
        
        # Test the process_resume function
        result = await process_resume(
            docx_file,
            "Software Engineer",
            "Python developer needed",
            "Test Corp",
            0.5
        )
        
        # Check the results
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], str)  # optimized text
        assert isinstance(result[1], str)  # changes
        assert isinstance(result[2], float)  # match score
        assert result[2] == 0.8  # match score from mock

@pytest.mark.asyncio
async def test_process_resume_no_file():
    # Test with no file
    result = await process_resume(
        None,
        "Software Engineer",
        "Python developer needed",
        "Test Corp",
        0.5
    )
    
    assert result[0] == "Error: Please upload a file."
    assert result[1] == ""
    assert result[2] == 0.0

@pytest.mark.asyncio
async def test_process_resume_unsupported_format(mock_file, mock_resume_optimizer, mock_document_parser):
    with patch('app.gradio_ui.resume_optimizer', mock_resume_optimizer), \
         patch('app.gradio_ui.DocumentParser', mock_document_parser):
        # Create a mock file with unsupported extension
        unsupported_file = mock_file(b"content", "test.txt")
        
        # Test the process_resume function
        result = await process_resume(
            unsupported_file,
            "Software Engineer",
            "Python developer needed",
            "Test Corp",
            0.5
        )
        
        assert result[0] == "Error: Unsupported file format. Please upload a PDF or DOCX file."
        assert result[1] == ""
        assert result[2] == 0.0

@pytest.mark.asyncio
async def test_process_resume_gradio_pdf(mock_gradio_file, sample_pdf_content, mock_resume_optimizer, mock_document_parser):
    with patch('app.gradio_ui.resume_optimizer', mock_resume_optimizer), \
         patch('app.gradio_ui.DocumentParser', mock_document_parser):
        # Create a mock Gradio PDF file
        pdf_file = mock_gradio_file(sample_pdf_content, "test.pdf")
        
        # Test the process_resume function
        result = await process_resume(
            pdf_file,
            "Software Engineer",
            "Python developer needed",
            "Test Corp",
            0.5
        )
        
        # Check the results
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], str)  # optimized text
        assert isinstance(result[1], str)  # changes
        assert isinstance(result[2], float)  # match score
        assert result[2] == 0.8  # match score from mock

@pytest.mark.asyncio
async def test_process_resume_gradio_docx(mock_gradio_file, sample_docx_content, mock_resume_optimizer, mock_document_parser):
    with patch('app.gradio_ui.resume_optimizer', mock_resume_optimizer), \
         patch('app.gradio_ui.DocumentParser', mock_document_parser):
        # Create a mock Gradio DOCX file
        docx_file = mock_gradio_file(sample_docx_content, "test.docx")
        
        # Test the process_resume function
        result = await process_resume(
            docx_file,
            "Software Engineer",
            "Python developer needed",
            "Test Corp",
            0.5
        )
        
        # Check the results
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], str)  # optimized text
        assert isinstance(result[1], str)  # changes
        assert isinstance(result[2], float)  # match score
        assert result[2] == 0.8  # match score from mock

@pytest.mark.asyncio
async def test_process_resume_gradio_named_string(mock_gradio_named_string, sample_pdf_content, mock_resume_optimizer, mock_document_parser):
    with patch('app.gradio_ui.resume_optimizer', mock_resume_optimizer), \
         patch('app.gradio_ui.DocumentParser', mock_document_parser):
        # Create a mock Gradio NamedString that points to a temporary file
        pdf_file = mock_gradio_named_string(sample_pdf_content, "test.pdf")
        
        # Test the process_resume function
        result = await process_resume(
            pdf_file,
            "Software Engineer",
            "Python developer needed",
            "Test Corp",
            0.5
        )
        
        # Check the results
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], str)  # optimized text
        assert isinstance(result[1], str)  # changes
        assert isinstance(result[2], float)  # match score
        assert result[2] == 0.8  # match score from mock