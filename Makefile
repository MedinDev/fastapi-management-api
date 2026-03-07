.PHONY: test install run clean

# Use the virtual environment binaries directly
PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest
UVICORN := .venv/bin/uvicorn

install:
	poetry install

test:
	$(PYTEST) tests/test_auth_integration.py

run:
	$(UVICORN) app.main:app --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
