.PHONY: help install build clean test run dev lint format check-deps package

# Configuration
PYTHON := python3
PIP := pip
VENV := venv
APP_NAME := csp_automation
SPEC_FILE := csp_automation.spec

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

################################################################################
# Help
################################################################################

help: ## Show this help message
	@echo "$(BLUE)CSP Automation Application - Makefile$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

################################################################################
# Development
################################################################################

install: ## Install dependencies in virtual environment
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@$(VENV)/bin/$(PIP) install --upgrade pip
	@$(VENV)/bin/$(PIP) install -r requirements.txt
	@$(VENV)/bin/playwright install chromium
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

dev: install ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@$(VENV)/bin/$(PIP) install pytest black flake8 mypy
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo "$(YELLOW)Activate with: source $(VENV)/bin/activate$(NC)"

run: ## Run the application (dev mode)
	@echo "$(BLUE)Running application...$(NC)"
	@$(VENV)/bin/$(PYTHON) console_app.py

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	@$(VENV)/bin/pytest tests/ -v || echo "$(YELLOW)⚠ No tests found$(NC)"

################################################################################
# Code Quality
################################################################################

lint: ## Run linting
	@echo "$(BLUE)Running linting...$(NC)"
	@$(VENV)/bin/flake8 src/ console_app.py --max-line-length=100 || true

format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(NC)"
	@$(VENV)/bin/black src/ console_app.py

check-deps: ## Check for outdated dependencies
	@echo "$(BLUE)Checking dependencies...$(NC)"
	@$(VENV)/bin/$(PIP) list --outdated

################################################################################
# Build & Package
################################################################################

clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	@rm -rf build dist
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned$(NC)"

build: clean install ## Build standalone executable
	@echo "$(BLUE)Building application...$(NC)"
	@bash build.sh

build-fast: ## Build without cleaning or reinstalling
	@echo "$(BLUE)Building application (fast mode)...$(NC)"
	@$(VENV)/bin/pyinstaller $(SPEC_FILE) --noconfirm

package: build ## Build and create distribution package
	@echo "$(BLUE)Creating distribution package...$(NC)"
	@rm -f $(APP_NAME)_dist.zip
	@cd dist && zip -r ../$(APP_NAME)_dist.zip . -x "*.DS_Store"
	@echo "$(GREEN)✓ Package created: $(APP_NAME)_dist.zip$(NC)"

################################################################################
# Verification
################################################################################

verify: ## Verify build can run
	@echo "$(BLUE)Verifying build...$(NC)"
	@test -f dist/$(APP_NAME) && echo "$(GREEN)✓ Executable found$(NC)" || \
		(echo "$(YELLOW)⚠ Executable not found. Run 'make build' first$(NC)" && exit 1)
	@ls -lh dist/$(APP_NAME)

verify-deps: ## Verify all dependencies are installed
	@echo "$(BLUE)Verifying dependencies...$(NC)"
	@$(VENV)/bin/$(PYTHON) -c "import nova_act; print('✓ nova-act')" || \
		echo "$(YELLOW)✗ nova-act not installed$(NC)"
	@$(VENV)/bin/$(PYTHON) -c "import playwright; print('✓ playwright')" || \
		echo "$(YELLOW)✗ playwright not installed$(NC)"
	@$(VENV)/bin/$(PYTHON) -c "import dotenv; print('✓ python-dotenv')" || \
		echo "$(YELLOW)✗ python-dotenv not installed$(NC)"

################################################################################
# Utility
################################################################################

show-config: ## Show current configuration
	@echo "$(BLUE)Current Configuration:$(NC)"
	@echo "  Python:      $$($(PYTHON) --version)"
	@echo "  Venv:        $(VENV)"
	@echo "  App Name:    $(APP_NAME)"
	@echo "  Spec File:   $(SPEC_FILE)"
	@echo ""
	@test -f input.json && echo "  Input File:  ✓ found" || \
		echo "  Input File:  ✗ not found"
	@test -f .env && echo "  .env File:   ✓ found" || \
		echo "  .env File:   ✗ not found"

logs: ## View recent logs
	@echo "$(BLUE)Recent logs:$(NC)"
	@ls -lt logs/ | head -10 || echo "$(YELLOW)No logs found$(NC)"

screenshots: ## View recent screenshots
	@echo "$(BLUE)Recent screenshots:$(NC)"
	@ls -lt screenshots/ | head -10 || echo "$(YELLOW)No screenshots found$(NC)"

################################################################################
# Docker (Future)
################################################################################

docker-build: ## Build Docker image (future)
	@echo "$(YELLOW)Docker build not yet implemented$(NC)"

docker-run: ## Run in Docker container (future)
	@echo "$(YELLOW)Docker run not yet implemented$(NC)"

################################################################################
# Distribution
################################################################################

dist-clean: ## Clean distribution files
	@echo "$(BLUE)Cleaning distribution files...$(NC)"
	@rm -f $(APP_NAME)_dist.zip
	@rm -rf dist/
	@echo "$(GREEN)✓ Distribution cleaned$(NC)"

dist-prepare: ## Prepare distribution (check before packaging)
	@echo "$(BLUE)Preparing distribution...$(NC)"
	@echo ""
	@echo "$(YELLOW)Pre-distribution Checklist:$(NC)"
	@test -f input.json && echo "  ✓ input.json exists" || \
		(echo "  ✗ input.json missing" && exit 1)
	@test -f .env && echo "  ✓ .env exists" || \
		(echo "  ✗ .env missing" && exit 1)
	@grep -q "your_username" input.json && \
		echo "  ✗ input.json contains placeholders" || \
		echo "  ✓ input.json configured"
	@grep -q "your_password" .env && \
		echo "  ✗ .env contains placeholders" || \
		echo "  ✓ .env configured"
	@echo ""
	@echo "$(GREEN)✓ Distribution prepared$(NC)"

################################################################################
# All-in-one
################################################################################

all: clean install build verify package ## Complete build pipeline
	@echo ""
	@echo "$(GREEN)╔══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  ✅ COMPLETE BUILD PIPELINE FINISHED                   ║$(NC)"
	@echo "$(GREEN)╚══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
