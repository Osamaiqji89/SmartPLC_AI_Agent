# Makefile for SmartPLC AI Agent

.PHONY: help install test lint format clean docker run

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "SmartPLC AI Agent - Development Commands"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .

install-dev: ## Install development dependencies
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest pytest-cov black ruff mypy pylint safety bandit

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=core --cov-report=html --cov-report=term

test-unit: ## Run unit tests only
	pytest tests/ -v -m "unit"

test-integration: ## Run integration tests only
	pytest tests/ -v -m "integration"

lint: ## Run linters
	black --check .
	ruff check .
	mypy core/ --ignore-missing-imports

format: ## Format code
	black .
	isort .
	ruff check --fix .

quality: ## Check code quality
	radon cc core/ -a -nb
	radon mi core/ -nb
	pylint core/ --output-format=colorized

security: ## Security scan
	safety check --file requirements.txt
	bandit -r core/ -f json -o bandit-report.json

clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.db" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf logs

docker-build: ## Build Docker image
	docker build -t plc-monitoring-studio:latest .

docker-run: ## Run Docker container
	docker-compose up -d

docker-stop: ## Stop Docker container
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

init-kb: ## Initialize knowledge base
	python init_knowledge_base.py

run: ## Run application
	python main.py

run-dev: ## Run in development mode
	DEBUG_MODE=true python main.py

docs: ## Build documentation
	mkdocs build

docs-serve: ## Serve documentation locally
	mkdocs serve

all: clean install init-kb test lint ## Clean, install, init, test, and lint
