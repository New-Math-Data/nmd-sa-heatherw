.PHONY: help init check test clean local-dev local-stop tf-init tf-plan tf-apply deploy-build ecs-deploy

.DEFAULT_GOAL := help

UV := uv
TF_DIR := infrastructure/live/candidate
DC := docker compose -f docker/docker-compose.yml

# Deployment configuration — set these before running deploy-build or ecs-deploy
# You can export them or pass on the command line: make deploy-build AWS_PROFILE=sa-assessment
AWS_REGION  ?= us-west-2
AWS_PROFILE ?= sa-assessment
AWS_ACCOUNT ?= $(shell aws sts get-caller-identity --profile $(AWS_PROFILE) --query Account --output text 2>/dev/null)
ECR_REPO    ?= $(shell cd $(TF_DIR) && terraform output -raw ecr_repository_url 2>/dev/null)
ECS_CLUSTER ?= $(shell aws ecs list-clusters --profile $(AWS_PROFILE) --region $(AWS_REGION) --query 'clusterArns[0]' --output text 2>/dev/null | xargs -I{} basename {})
ECS_SERVICE ?= $(shell aws ecs list-services --cluster $(ECS_CLUSTER) --profile $(AWS_PROFILE) --region $(AWS_REGION) --query 'serviceArns[0]' --output text 2>/dev/null | xargs -I{} basename {})

# Colors
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

##@ General
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(BLUE)Usage:$(RESET)\n  make $(GREEN)<target>$(RESET)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(RESET)\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Setup
init: ## Initialize project (install uv + deps)
	@command -v uv >/dev/null 2>&1 || { echo "$(BLUE)Installing uv...$(RESET)"; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	@echo "$(YELLOW)✓  Running uv sync$(RESET)"
	$(UV) sync --all-groups
	@echo "$(GREEN)✓ Project initialized$(RESET)"

##@ Quality
check: ## Run all checks (format, lint, typecheck)
	@echo "$(YELLOW)✓  Formatting$(RESET)"
	$(UV) run ruff format --check .
	@echo "$(YELLOW)✓  Linting$(RESET)"
	$(UV) run ruff check .
	@echo "$(YELLOW)✓  Type checking$(RESET)"
	$(UV) run mypy
	@echo "$(GREEN)✓ All checks passed$(RESET)"

test: ## Run tests with coverage
	$(UV) run pytest --cov=src --cov-report=term-missing --cov-fail-under=80

##@ Local Development
local-dev: ## Start local dev environment (Docker Compose)
	@echo "$(BLUE)Starting local development environment...$(RESET)"
	$(DC) build --no-cache api
	$(DC) up -d db
	@echo "$(BLUE)Waiting for database...$(RESET)"
	@until $(DC) exec db pg_isready -U appuser -d appdb > /dev/null 2>&1; do sleep 1; done
	@echo "$(GREEN)Database ready$(RESET)"
	$(DC) up -d api
	@echo "$(GREEN)Local environment ready — API: http://localhost:8080/docs$(RESET)"
	$(DC) logs -f api

local-stop: ## Stop local services
	$(DC) down
	@echo "$(GREEN)Stopped$(RESET)"

##@ Terraform
tf-init: ## Initialize Terraform
	@echo "$(BLUE)Initializing Terraform...$(RESET)"
	cd $(TF_DIR) && terraform init

tf-plan: ## Plan Terraform changes
	@echo "$(BLUE)Planning Terraform...$(RESET)"
	cd $(TF_DIR) && terraform plan -out=tfplan

tf-apply: ## Apply Terraform changes
	@echo "$(YELLOW)Applying Terraform...$(RESET)"
	cd $(TF_DIR) && terraform apply tfplan

##@ Deployment
deploy-build: ## Build and push Docker image to ECR
	@echo "$(BLUE)Building and pushing image...$(RESET)"
	@echo "  ECR_REPO: $(ECR_REPO)"
	@echo "  REGION:   $(AWS_REGION)"
	@echo "  PROFILE:  $(AWS_PROFILE)"
	aws ecr get-login-password --region $(AWS_REGION) --profile $(AWS_PROFILE) | \
		docker login --username AWS --password-stdin $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker build --platform linux/amd64 -f docker/Dockerfile -t $(ECR_REPO):latest .
	docker push $(ECR_REPO):latest
	@echo "$(GREEN)✓ Image pushed$(RESET)"

ecs-deploy: ## Force new ECS deployment
	@echo "  CLUSTER: $(ECS_CLUSTER)"
	@echo "  SERVICE: $(ECS_SERVICE)"
	aws ecs update-service --cluster $(ECS_CLUSTER) --service $(ECS_SERVICE) --force-new-deployment \
		--profile $(AWS_PROFILE) --region $(AWS_REGION) --no-cli-pager
	@echo "$(GREEN)✓ ECS deployment initiated$(RESET)"

##@ Utilities
clean: ## Clean build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	rm -rf dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned$(RESET)"
