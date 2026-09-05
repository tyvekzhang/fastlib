.PHONY: help install lint test build publish clean

SOURCE_DIR = fastlib
PYTHON_VERSION = 3.11

help:
	@echo "Available make targets:"
	@echo "  install               Install project dependencies using uv"
	@echo "  lint                  Perform static code analysis"
	@echo "  test                  Run unit tests with coverage"
	@echo "  build                 Build distribution packages"
	@echo "  publish               Publish package to PyPI"
	@echo "  clean                 Remove temporary files and build artifacts"
	@echo ""
	@echo "Use 'make <target>' to run a specific command."

install:
	uv sync

lint:
	uv sync --group dev
	uv run pre-commit run --all-files --verbose

test:
	uv sync --group dev
	uv run coverage run -m pytest tests && \
	uv run coverage html

build: clean
	@echo "Building distribution packages..."
	uv build

publish: build
	@echo "Publishing to PyPI..."
	uv publish

# Windows make typically uses Git Bash as SHELL; use portable rm (not cmd.exe).
clean:
ifeq ($(OS),Windows_NT)
	@echo "Cleaning on Windows..."
else
	@echo "Cleaning on Unix/Linux..."
endif
	rm -rf dist/ \
	    build/ \
	    coverage/ \
	    *.egg-info \
	    $(SOURCE_DIR)/htmlcov \
	    $(SOURCE_DIR)/log \
	    $(SOURCE_DIR)/__pycache__ \
	    **/__pycache__ \
	    .pytest_cache \
	    .ruff_cache
