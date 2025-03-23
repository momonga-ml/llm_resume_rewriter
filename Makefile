.PHONY: install test lint run clean

# Default Python interpreter
PYTHON := python

# Install dependencies
install:
	$(PYTHON) -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest ruff

# Run tests
test:
	pytest

# Run linting
lint:
	ruff check .

# Run the application
run:
	uvicorn app.main:app --reload

# Clean up Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".pytest_cache" -delete
	find . -type f -name ".ruff_cache" -delete

# Run both tests and linting
check: test lint 