SHELL := /bin/bash

COLOR_RESET=\033[0m
COLOR_CYAN=\033[1;36m
COLOR_GREEN=\033[1;32m

SRC_DIR = src
TEST_DIR = tests
PACKAGE = droid_dash
VENV = .venv/bin

.PHONY: help install create-venv install-deps clean test coverage coverage-show format lint lint-stats fix type bandit changelog docs docs-serve build run

.DEFAULT_GOAL := help

.SILENT:

help: ## Show all Makefile targets.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'

install: create-venv install-deps ## Create virtual environment and install dependencies.
	@echo -e "$(COLOR_GREEN)All done!$(COLOR_RESET)"

create-venv: ## Create a virtual environment using uv.
	@echo -e "$(COLOR_CYAN)Creating virtual environment...$(COLOR_RESET)"
	uv venv --python 3.11
	uv python pin 3.11

install-deps: ## Install dependencies (including dev).
	@echo -e "$(COLOR_CYAN)Installing dependencies...$(COLOR_RESET)"
	uv sync --group dev --group docs

clean: ## Clean up pycache, pyc files, and build artifacts.
	@echo -e "$(COLOR_CYAN)Cleaning up...$(COLOR_RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf dist/ build/ *.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/ htmlcov/ site/

test: ## Run tests with pytest.
	@echo -e "$(COLOR_CYAN)Running tests...$(COLOR_RESET)"
	PYTHONPATH=$(SRC_DIR) $(VENV)/pytest $(TEST_DIR)/ -v

coverage: ## Run tests with coverage report.
	@echo -e "$(COLOR_CYAN)Running tests with coverage...$(COLOR_RESET)"
	PYTHONPATH=$(SRC_DIR) $(VENV)/pytest --cov=$(PACKAGE) --cov-report=html --cov-report=term-missing $(TEST_DIR)/

coverage-show: ## Open coverage report in browser.
	@echo -e "$(COLOR_CYAN)Opening coverage report...$(COLOR_RESET)"
	@if [ "$$(uname)" = "Darwin" ]; then open htmlcov/index.html; \
	elif [ "$$(uname)" = "Linux" ]; then xdg-open htmlcov/index.html; fi

format: ## Format code with ruff.
	@echo -e "$(COLOR_CYAN)Formatting code...$(COLOR_RESET)"
	$(VENV)/ruff format $(SRC_DIR) $(TEST_DIR)
	$(VENV)/ruff check $(SRC_DIR) $(TEST_DIR) --fix --unsafe-fixes

lint: ## Check code style with ruff.
	@echo -e "$(COLOR_CYAN)Linting code...$(COLOR_RESET)"
	$(VENV)/ruff check $(SRC_DIR) $(TEST_DIR)

lint-stats: ## Show ruff violation statistics.
	@echo -e "$(COLOR_CYAN)Ruff statistics...$(COLOR_RESET)"
	$(VENV)/ruff check $(SRC_DIR) $(TEST_DIR) --statistics

fix: ## Auto-fix ruff issues.
	@echo -e "$(COLOR_CYAN)Fixing code issues...$(COLOR_RESET)"
	$(VENV)/ruff check $(SRC_DIR) $(TEST_DIR) --fix

type: ## Run type checker (mypy).
	@echo -e "$(COLOR_CYAN)Type checking...$(COLOR_RESET)"
	$(VENV)/mypy $(SRC_DIR)/$(PACKAGE) --ignore-missing-imports

bandit: ## Run security linter.
	@echo -e "$(COLOR_CYAN)Running bandit...$(COLOR_RESET)"
	$(VENV)/bandit -r $(SRC_DIR) -ll -ii

docs: ## Build documentation with mkdocs.
	@echo -e "$(COLOR_CYAN)Building documentation...$(COLOR_RESET)"
	$(VENV)/mkdocs build

docs-serve: ## Serve documentation locally.
	@echo -e "$(COLOR_CYAN)Serving documentation at http://127.0.0.1:8000...$(COLOR_RESET)"
	$(VENV)/mkdocs serve

build: ## Build the package.
	@echo -e "$(COLOR_CYAN)Building package...$(COLOR_RESET)"
	uv build

run: ## Run the TUI dashboard.
	@echo -e "$(COLOR_CYAN)Starting dashboard...$(COLOR_RESET)"
	PYTHONPATH=$(SRC_DIR) $(VENV)/python -m $(PACKAGE).cli

changelog: ## Generate changelog using git-cliff.
	git-cliff -o CHANGELOG.md
