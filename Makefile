# ==============================================
# AI CLAIMS - MULTI-ENVIRONMENT MAKEFILE
# ==============================================

.PHONY: help local prod stop restart logs clean build status check-env

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help:
	@echo "$(BLUE)🚀 AI Claims - Environment Manager$(NC)"
	@echo ""
	@echo "$(GREEN)Quick Start:$(NC)"
	@echo "  make local     - Start LOCAL development environment"
	@echo "  make prod      - Start PRODUCTION environment"
	@echo ""
	@echo "$(GREEN)Management:$(NC)"
	@echo "  make stop      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - Show logs (all services)"
	@echo "  make status    - Show container status"
	@echo ""
	@echo "$(GREEN)Build & Clean:$(NC)"
	@echo "  make build     - Rebuild all images"
	@echo "  make clean     - Stop and remove all containers & volumes"
	@echo ""
	@echo "$(GREEN)Individual Services:$(NC)"
	@echo "  make logs-frontend    - Frontend logs"
	@echo "  make logs-backend     - Backend logs"
	@echo "  make logs-worker      - Worker logs"
	@echo "  make restart-frontend - Restart frontend"
	@echo "  make restart-backend  - Restart backend"

check-env:
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ .env file not found!$(NC)"; \
		echo "$(YELLOW)💡 Run 'make local' or 'make prod' to create it$(NC)"; \
		exit 1; \
	fi

local:
	@echo "$(BLUE)🏠 Starting LOCAL development environment...$(NC)"
	@if [ ! -f .env.local ]; then \
		echo "$(YELLOW)⚠️  .env.local not found, copying from .env.example$(NC)"; \
		cp .env.example .env.local; \
		echo "$(YELLOW)📝 Please edit .env.local with your credentials$(NC)"; \
	fi
	@cp .env.local .env
	@docker compose -f docker-compose.yml -f docker-compose.local.yml up -d
	@echo "$(GREEN)✅ Local environment started!$(NC)"
	@echo ""
	@echo "$(GREEN)🌐 URLs:$(NC)"
	@echo "  Frontend:  http://localhost:3000"
	@echo "  Backend:   http://localhost:8000"
	@echo "  API Docs:  http://localhost:8000/api/v1/docs"
	@echo "  MinIO:     http://localhost:9001 (admin/minioadmin123)"
	@echo ""
	@echo "$(YELLOW)💡 Tip: Run 'make logs' to see logs$(NC)"

prod:
	@echo "$(BLUE)🌍 Starting PRODUCTION environment...$(NC)"
	@if [ ! -f .env.production ]; then \
		echo "$(RED)❌ .env.production not found!$(NC)"; \
		echo "$(YELLOW)Creating from template...$(NC)"; \
		cp .env.example .env.production; \
		echo "$(RED)⚠️  IMPORTANT: Edit .env.production with PRODUCTION credentials!$(NC)"; \
		exit 1; \
	fi
	@cp .env.production .env
	@docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✅ Production environment started!$(NC)"
	@echo ""
	@echo "$(YELLOW)💡 Tip: Run 'make logs' to monitor$(NC)"

stop:
	@echo "$(YELLOW)🛑 Stopping all services...$(NC)"
	@docker compose down
	@echo "$(GREEN)✅ All services stopped$(NC)"

restart: stop
	@if [ -f .env ]; then \
		if grep -q "ENVIRONMENT=development" .env; then \
			make local; \
		else \
			make prod; \
		fi \
	else \
		echo "$(RED)❌ No .env found. Run 'make local' or 'make prod'$(NC)"; \
	fi

logs:
	@docker compose logs -f

logs-frontend:
	@docker compose logs -f frontend

logs-backend:
	@docker compose logs -f backend

logs-worker:
	@docker compose logs -f worker

status:
	@echo "$(BLUE)📊 Container Status:$(NC)"
	@docker compose ps

build:
	@echo "$(BLUE)🔨 Rebuilding all images...$(NC)"
	@docker compose build --no-cache
	@echo "$(GREEN)✅ Build complete!$(NC)"

rebuild-frontend:
	@echo "$(BLUE)🔨 Rebuilding frontend...$(NC)"
	@docker compose build --no-cache frontend
	@docker compose up -d frontend
	@echo "$(GREEN)✅ Frontend rebuilt!$(NC)"

rebuild-backend:
	@echo "$(BLUE)🔨 Rebuilding backend...$(NC)"
	@docker compose build --no-cache backend
	@docker compose up -d backend
	@echo "$(GREEN)✅ Backend rebuilt!$(NC)"

restart-frontend:
	@docker compose restart frontend

restart-backend:
	@docker compose restart backend

restart-worker:
	@docker compose restart worker

clean:
	@echo "$(RED)🧹 Cleaning all containers and volumes...$(NC)"
	@read -p "Are you sure? This will delete ALL data! (y/N) " confirm && [ $$confirm = y ] || exit 1
	@docker compose down -v
	@rm -rf ./frontend/.next
	@rm -f .env
	@echo "$(GREEN)✅ Cleaned!$(NC)"

shell-backend:
	@docker compose exec backend bash

shell-frontend:
	@docker compose exec frontend sh

shell-db:
	@docker compose exec db psql -U claims_user -d claims_db

db-backup:
	@echo "$(BLUE)💾 Creating database backup...$(NC)"
	@docker compose exec db pg_dump -U claims_user claims_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Backup created!$(NC)"
