# Resume Rewriter LLM

An intelligent application that helps rewrite resumes to better match job descriptions using Large Language Models.

## Features

- Resume parsing (PDF and DOCX support)
- Job description analysis
- AI-powered resume rewriting
- Format preservation
- Customizable optimization strategies

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:
- Windows:
```bash
.venv\Scripts\activate
```
- Unix/MacOS:
```bash
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_api_key_here
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
.
├── app/
│   ├── api/            # API routes
│   ├── core/           # Core application logic
│   ├── models/         # Data models
│   ├── services/       # Business logic
│   └── utils/          # Utility functions
├── tests/              # Test files
├── docs/               # Documentation
├── requirements.txt    # Project dependencies
└── README.md          # Project documentation
```

## Usage

1. Upload your resume (PDF or DOCX format)
2. Paste the job description
3. Configure optimization preferences
4. Get your optimized resume

## Development

The project uses:
- FastAPI for the backend
- LangChain for LLM integration
- Python-DOCX and PyPDF for document handling 