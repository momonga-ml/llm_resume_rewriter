from setuptools import setup, find_packages

setup(
    name="resume_rewriter_llm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-multipart",
        "pydantic",
        "python-dotenv",
        "langchain",
        "langchain-openai",
        "python-docx",
        "pypdf",
        "gradio",
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-asyncio",
            "pytest-mock",
        ],
    },
) 