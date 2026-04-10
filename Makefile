.PHONY: help install dev lint format test test-cov clean docker-build docker-up docker-down server cli migrate seed

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)KHOps Development Commands$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install -e ".[dev]"
	pre-commit install

dev: ## Install in development mode
	pip install -e ".[dev]"

lint: ## Run linting checks
	@echo "$(BLUE)Running linting checks...$(NC)"
	isort --check-only khops tests
	black --check khops tests
	flake8 khops tests
	mypy khops

format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	isort khops tests
	black khops tests

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	pytest tests/ -m "not slow" -x

test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest tests/ --cov=khops --cov-report=html --cov-report=term-missing

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest tests/unit/ -v

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests
	@echo "$(BLUE)Running E2E tests...$(NC)"
	pytest tests/e2e/ -v

test-all: ## Run all tests including slow tests
	@echo "$(BLUE)Running all tests...$(NC)"
	pytest tests/ -v

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	bandit -r khops -ll

clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	rm -rf build/ dist/ *.egg-info .mypy_cache .pytest_cache htmlcov .coverage

server: ## Start FastAPI server
	@echo "$(GREEN)Starting KHOps Server (http://localhost:8000)$(NC)"
	uvicorn khops.server.app:app --reload --host 0.0.0.0 --port 8000

cli: ## Interactive CLI
	@echo "$(GREEN)Starting KHOps CLI$(NC)"
	khops

migrate: ## Run database migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	alembic upgrade head

seed: ## Seed database with sample data
	@echo "$(BLUE)Seeding database...$(NC)"
	python scripts/seed_db.py

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t khops:latest -f docker/Dockerfile .

docker-up: ## Start Docker services
	@echo "$(GREEN)Starting Docker services...$(NC)"
	docker-compose -f docker/docker-compose.yml up -d

docker-down: ## Stop Docker services
	@echo "$(BLUE)Stopping Docker services...$(NC)"
	docker-compose -f docker/docker-compose.yml down

docker-logs: ## View Docker logs
	docker-compose -f docker/docker-compose.yml logs -f

docker-clean: ## Remove Docker containers and volumes
	@echo "$(RED)Removing Docker containers and volumes...$(NC)"
	docker-compose -f docker/docker-compose.yml down -v

setup-dev: install lint format ## Complete dev setup with install, lint, and format

db-create: ## Create database
	@echo "$(BLUE)Creating database...$(NC)"
	python -c "from khops.db.session import engine; engine.execute('CREATE DATABASE IF NOT EXISTS khops;')"

db-reset: ## Reset database (WARNING: Deletes all data)
	@echo "$(RED)Resetting database...$(NC)"
	alembic downgrade base
	alembic upgrade head
	make seed

docs-build: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	cd docs && make html

version: ## Show project version
	@python -c "import khops; print(khops.__version__)" 2>/dev/null || echo "KHOps 0.1.0"
