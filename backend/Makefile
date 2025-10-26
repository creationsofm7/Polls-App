
.PHONY: run test lint format

# Default command
all: run

# Run the FastAPI server with auto-reload
run:
    poetry run uvicorn main:app --reload

# Run tests with pytest
test:
    poetry run pytest

# Lint the code
lint:
    poetry run ruff check .

# Format the code
format:
    poetry run black .
