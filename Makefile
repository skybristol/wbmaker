.PHONY: help install test coverage lint format clean build

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	poetry install

test:  ## Run tests
	poetry run pytest -v

coverage:  ## Run tests with coverage report
	poetry run pytest --cov=wbmaker --cov-report=html --cov-report=term

lint:  ## Run all linters
	poetry run ruff check wbmaker/ tests/
	poetry run black --check wbmaker/ tests/
	poetry run mypy wbmaker/ --ignore-missing-imports

format:  ## Format code with black and ruff
	poetry run black wbmaker/ tests/
	poetry run ruff check wbmaker/ tests/ --fix

clean:  ## Remove build artifacts and cache
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	poetry build

check:  ## Run all checks (format, lint, test)
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) test

dev: install  ## Set up development environment
	@echo "Development environment ready!"
	@echo "Run 'poetry shell' to activate the virtual environment"
