.PHONY: help build up down logs restart ps shell-backend migrate clean rebuild health

help:
	@echo "AI Claims - Makefile Commands"
	@echo "================================"
	@echo "make build        - Build Docker images"
	@echo "make up           - Start all services"
	@echo "make down         - Stop all services"
	@echo "make restart      - Restart all services"
	@echo "make logs         - Show logs (all services)"
	@echo "make ps           - Show running containers"
	@echo "make health       - Check health of all services"
	@echo "make migrate      - Run database migrations"
	@echo "make shell-backend- Open shell in backend container"
	@echo "make clean        - Remove all containers, volumes, images"
	@echo "make rebuild      - Full rebuild (clean + build + up)"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

ps:
	docker compose ps

shell-backend:
	docker compose exec backend bash

migrate:
	docker compose exec backend python scripts/migrate_db.py

health:
	@echo "Checking service health..."
	@echo "\n📡 Backend:"
	@curl -f http://localhost:8000/claims/ || echo "❌ Backend not responding"
	@echo "\n📡 Presidio:"
	@curl -f http://localhost:8001/health || echo "❌ Presidio not responding"
	@echo "\n📡 Redis:"
	@docker compose exec redis redis-cli ping || echo "❌ Redis not responding"
	@echo "\n📊 Container status:"
	@docker compose ps

clean:
	docker compose down -v
	docker system prune -f

rebuild: clean build up
	@echo "✅ Full rebuild complete"
