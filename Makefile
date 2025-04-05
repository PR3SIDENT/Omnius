.PHONY: build run stop logs clean test help

# Default target
.DEFAULT_GOAL := help

# Variables
DOCKER_COMPOSE = docker-compose
CONTAINER_NAME = omnius-bot

help: ## Show this help message
	@echo 'Usage:'
	@echo '  make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial setup of the project
	cp .env.example .env
	mkdir -p data/knowledge/{messages,vector_store} logs
	@echo "Please edit .env file with your credentials"

build: ## Build the Docker image
	$(DOCKER_COMPOSE) build

run: ## Start the bot
	$(DOCKER_COMPOSE) up -d

stop: ## Stop the bot
	$(DOCKER_COMPOSE) down

restart: ## Restart the bot
	$(DOCKER_COMPOSE) restart

logs: ## Show bot logs
	$(DOCKER_COMPOSE) logs -f

clean: ## Remove all containers, volumes, and data
	$(DOCKER_COMPOSE) down -v
	rm -rf data/* logs/*

update: ## Update the bot (rebuild and restart)
	git pull
	$(DOCKER_COMPOSE) build
	$(DOCKER_COMPOSE) up -d

status: ## Check bot status
	$(DOCKER_COMPOSE) ps
	@echo "\nHealth Check:"
	@docker exec $(CONTAINER_NAME) python3 -c "from health import check_health; print(check_health())"

prune: ## Remove unused Docker resources
	docker system prune -f

volumes: ## List volumes and their sizes
	@docker system df -v

backup: ## Backup data directory
	tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz data/

restore: ## Restore data from backup (specify BACKUP=filename)
	@if [ -z "$(BACKUP)" ]; then \
		echo "Please specify backup file: make restore BACKUP=filename"; \
		exit 1; \
	fi
	tar -xzf $(BACKUP) -C ./ 