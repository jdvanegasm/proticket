# ============================================================
# ProTicket Infrastructure Makefile
# ============================================================

# ─────────────────────────────
# Global Variables
# ─────────────────────────────
DBS_COMPOSE_FILE     = docker-compose.dbs.yaml
BACKEND_COMPOSE_FILE = docker-compose.backend.yaml
ENV_FILE             = .env

# ─────────────────────────────
# Default Help Menu
# ─────────────────────────────
.PHONY: help
help:
	@echo "ProTicket Stack Management"
	@echo ""
	@echo "Database Stack Commands:"
	@echo "  make up-dbs        → Build and start MySQL + PostgreSQL stack"
	@echo "  make down-dbs      → Stop database containers (preserve volumes)"
	@echo "  make clean-dbs     → Remove containers + volumes (!!!full reset!!!)"
	@echo "  make logs-dbs      → Follow DB logs"
	@echo "  make status-dbs    → Show DB containers"
	@echo "  make mysql         → Enter MySQL shell"
	@echo "  make postgres      → Enter PostgreSQL shell"
	@echo ""
	@echo "Backend Stack Commands:"
	@echo "  make up-backend    → Build and start backend microservices"
	@echo "  make down-backend  → Stop backend containers"
	@echo "  make restart-auth  → Restart only the Auth microservice"
	@echo "  make logs-auth     → Show logs for Auth microservice"
	@echo "  make status        → Show all running containers"
	@echo ""
	@echo "Combined Commands:"
	@echo "  make up-all        → Start databases + backend"
	@echo "  make down-all      → Stop all stacks"
	@echo "  make clean-all     → Remove all containers + volumes"

# ============================================================
# DATABASE STACK
# ============================================================

.PHONY: up-dbs
up-dbs:
	@echo "Starting database stack..."
	docker compose -f $(DBS_COMPOSE_FILE) --env-file $(ENV_FILE) up --build -d

.PHONY: down-dbs
down-dbs:
	@echo "Stopping database stack (containers only)..."
	docker compose -f $(DBS_COMPOSE_FILE) down

.PHONY: clean-dbs
clean-dbs:
	@echo "Removing DB containers, networks, and volumes..."
	docker compose -f $(DBS_COMPOSE_FILE) down -v
	@echo "Database environment cleaned."

.PHONY: logs-dbs
logs-dbs:
	@echo "Showing database logs (Ctrl+C to exit)..."
	docker compose -f $(DBS_COMPOSE_FILE) logs -f

.PHONY: status-dbs
status-dbs:
	@echo "Active database containers:"
	docker ps --filter "name=mysql_auth" --filter "name=postgres_business" --filter "name=pgadmin_business" --filter "name=phpmyadmin_auth"

.PHONY: mysql
mysql:
	@echo "Opening MySQL shell..."
	docker exec -it mysql_auth mysql -u$$(grep MYSQL_USER $(ENV_FILE) | cut -d '=' -f2) -p$$(grep MYSQL_PASSWORD $(ENV_FILE) | cut -d '=' -f2) $$(grep MYSQL_DATABASE $(ENV_FILE) | cut -d '=' -f2)

.PHONY: postgres
postgres:
	@echo "Opening PostgreSQL shell..."
	docker exec -it postgres_business psql -U $$(grep POSTGRES_USER $(ENV_FILE) | cut -d '=' -f2) -d $$(grep POSTGRES_DB $(ENV_FILE) | cut -d '=' -f2)

# ============================================================
# BACKEND STACK (Microservices)
# ============================================================

.PHONY: up-backend
up-backend:
	@echo "Starting backend services..."
	docker compose -f $(BACKEND_COMPOSE_FILE) --env-file $(ENV_FILE) up --build -d

.PHONY: down-backend
down-backend:
	@echo "Stopping backend services..."
	docker compose -f $(BACKEND_COMPOSE_FILE) down

.PHONY: restart-auth
restart-auth:
	@echo "Restarting Auth microservice..."
	docker compose -f $(BACKEND_COMPOSE_FILE) restart auth_service

.PHONY: logs-auth
logs-auth:
	@echo "Showing logs for Auth microservice..."
	docker logs -f auth_service

# ============================================================
# COMBINED COMMANDS
# ============================================================

.PHONY: up-all
up-all: up-dbs up-backend

.PHONY: down-all
down-all: down-backend down-dbs

.PHONY: clean-all
clean-all: clean-dbs
	@echo "Removing all backend containers..."
	docker compose -f $(BACKEND_COMPOSE_FILE) down -v
	@echo "Full cleanup done."

.PHONY: status
status:
	@echo "Full container status:"
	docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"