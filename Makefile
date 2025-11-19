.PHONY: build up down logs shell-backend

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

shell-backend:
	docker-compose exec backend bash

deploy-scw:
	@echo "Deploying to Scaleway..."
	@echo "1. Ensure you have provisioned a VM (Stardust or Learning Instance)."
	@echo "2. Copy files to VM: scp -r . root@<VM_IP>:/root/app"
	@echo "3. SSH into VM: ssh root@<VM_IP>"
	@echo "4. Install Docker & Compose"
	@echo "5. Run 'make up'"
