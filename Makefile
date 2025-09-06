.PHONY: help install db dp dev start lint test image clean

# Variables
SERVER_LOG = fast-web.log
SOURCE_DIR = src

help:
	@echo "Available make targets:"
	@echo "  install               Install project dependencies using uv"
	@echo "  db                    Generate db structure"
	@echo "  dp                    Upgrade db structure"
	@echo "  dev                   Development environment startup"
	@echo "  start                 Production environment startup"
	@echo "  lint                  Perform static code analysis"
	@echo "  test                  Run unit tests"
	@echo "  image                 Build the Docker image for the project"
	@echo "  push                  Push Docker image to dockerHub"
	@echo "  clean                 Remove temporary files"
	@echo ""
	@echo "Use 'make <target>' to run a specific command."

install:
	uv sync

db:
	uv run alembic revision --autogenerate

dp:
	uv run alembic upgrade head

dev: install
	uv run alembic upgrade head && \
	uv run main.py

start: install
	uv run alembic upgrade head && \
	nohup uv run main.py --env prod > $(SERVER_LOG) 2>&1 &

lint:
	uv add pre-commit --group dev && \
	uv run pre-commit run --all-files --verbose

test:
	uv sync --group dev && \
	uv run alembic upgrade head && \
	cd $(SOURCE_DIR) && \
	uv run coverage run -m pytest tests && \
	uv run coverage html

ifeq ($(OS),Windows_NT)
clean:
	@echo "Cleaning on Windows..."
	@if exist dist rmdir /s /q dist 2>nul || echo "dist not found, skipping"
	@if exist $(DOCS_DIR)\build rmdir /s /q $(DOCS_DIR)\build 2>nul
	@if exist $(SOURCE_DIR)\htmlcov rmdir /s /q $(SOURCE_DIR)\htmlcov 2>nul
	@if exist $(SOURCE_DIR)\log rmdir /s /q $(SOURCE_DIR)\log 2>nul
	@if exist $(SOURCE_DIR)\.coverage del /q $(SOURCE_DIR)\.coverage 2>nul

else
clean:
	rm -rf dist \
	    $(DOCS_DIR)/build \
	    $(SOURCE_DIR)/htmlcov \
	    $(SOURCE_DIR)/.coverage* \

endif

image: clean
	docker build -t $(DOCKERHUB_USER)/$(RELEASE_NAME):$(TAG) .
