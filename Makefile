.PHONY: help install lint test build publish clean

# Variables
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
	uv run alembic upgrade head
	cd $(SOURCE_DIR) && \
	uv run coverage run -m pytest tests && \
	uv run coverage html

build: clean
	@echo "Building distribution packages..."
	uv build

publish: build
	@echo "Publishing to PyPI..."
	uv publish

ifeq ($(OS),Windows_NT)
clean:
	@echo "Cleaning on Windows..."
	@if exist dist rmdir /s /q dist 2>nul || echo "dist not found, skipping"
	@if exist build rmdir /s /q build 2>nul || echo "build not found, skipping"
	@for /d %%d in (*.egg-info) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
	@if exist $(SOURCE_DIR)\htmlcov rmdir /s /q $(SOURCE_DIR)\htmlcov 2>nul
	@if exist $(SOURCE_DIR)\log rmdir /s /q $(SOURCE_DIR)\log 2>nul
	@if exist $(SOURCE_DIR)\.coverage del /q $(SOURCE_DIR)\.coverage 2>nul
	@if exist $(SOURCE_DIR)\__pycache__ rmdir /s /q $(SOURCE_DIR)\__pycache__ 2>nul
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
else
clean:
	@echo "Cleaning on Unix/Linux..."
	rm -rf dist/ \
	    build/ \
	    *.egg-info \
	    $(SOURCE_DIR)/htmlcov \
	    $(SOURCE_DIR)/.coverage* \
	    $(SOURCE_DIR)/log \
	    $(SOURCE_DIR)/__pycache__ \
	    **/__pycache__ \
	    .pytest_cache \
	    .ruff_cache
endif
