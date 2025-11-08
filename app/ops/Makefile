# Variables
COMPOSE_FILE = docker-compose.dbs.yaml
ENV_FILE     = .env

# Default target
.PHONY: help
help:
	@echo "ProTicket Database Stack Commands:"
	@echo "  make up        → Build and start all DB containers"
	@echo "  make down      → Stop and remove containers (keep data)"
	@echo "  make restart   → Restart the database stack"
	@echo "  make clean     → Remove containers + volumes (!!!full reset!!!)"
	@echo "  make logs      → Follow PostgreSQL and MySQL logs"
	@echo "  make status    → Show running containers"
	@echo "  make mysql     → Enter MySQL shell"
	@echo "  make postgres  → Enter PostgreSQL shell"

# Start services
.PHONY: up
up:
	@echo "Starting database stack..."
	docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) up --build -d

# Stop services (preserve data)
.PHONY: down
down:
	@echo "Stopping database stack (containers only)..."
	docker compose -f $(COMPOSE_FILE) down

# Restart the stack
.PHONY: restart
restart: down up

# Remove everything (containers + volumes)
.PHONY: clean
clean:
	@echo "Removing containers, networks, and volumes..."
	docker compose -f $(COMPOSE_FILE) down -v
	@echo "Clean environment ready."

# Show logs
.PHONY: logs
logs:
	@echo "Showing database logs (Ctrl+C to exit)..."
	docker compose -f $(COMPOSE_FILE) logs -f

# Check running containers
.PHONY: status
status:
	@echo "Active containers:"
	docker ps --filter "name=mysql_auth" --filter "name=postgres_business" --filter "name=pgadmin_business" --filter "name=phpmyadmin_auth"

# Open MySQL shell
.PHONY: mysql
mysql:
	@echo "Opening MySQL shell..."
	docker exec -it mysql_auth mysql -u$$(grep MYSQL_USER $(ENV_FILE) | cut -d '=' -f2) -p$$(grep MYSQL_PASSWORD $(ENV_FILE) | cut -d '=' -f2) $$(grep MYSQL_DATABASE $(ENV_FILE) | cut -d '=' -f2)

# Open PostgreSQL shell
.PHONY: postgres
postgres:
	@echo "Opening PostgreSQL shell..."
	docker exec -it postgres_business psql -U $$(grep POSTGRES_USER $(ENV_FILE) | cut -d '=' -f2) -d $$(grep POSTGRES_DB $(ENV_FILE) | cut -d '=' -f2)