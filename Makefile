# Makefile para Badg3rFuzz
.PHONY: help install install-dev test test-unit test-integration test-security test-performance
.PHONY: lint security-check clean build docker-build docker-run coverage docs
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip3
VENV := venv
PYTEST := pytest
PROJECT_NAME := badg3rfuzz

# Colores para output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Mostrar esta ayuda
	@echo "$(GREEN)Badg3rFuzz - Makefile Commands$(NC)"
	@echo "=================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ===== INSTALACIÓN =====
install: ## Instalar dependencias de producción
	@echo "$(GREEN)Installing production dependencies...$(NC)"
	$(PIP) install -r requirements.txt

install-dev: ## Instalar dependencias de desarrollo
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	$(PIP) install -r requirements.txt -r requirements-dev.txt
	pre-commit install

venv: ## Crear entorno virtual
	@echo "$(GREEN)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(YELLOW)Activate with: source $(VENV)/bin/activate$(NC)"

setup: venv install-dev ## Setup completo del proyecto
	@echo "$(GREEN)Setting up test environment...$(NC)"
	bash scripts/setup-test-env.sh

# ===== TESTING =====
test: ## Ejecutar todos los tests
	@echo "$(GREEN)Running all tests...$(NC)"
	$(PYTEST) tests/ -v

test-unit: ## Ejecutar tests unitarios
	@echo "$(GREEN)Running unit tests...$(NC)"
	$(PYTEST) tests/test_*.py -v -m "not integration and not security and not benchmark"

test-integration: ## Ejecutar tests de integración
	@echo "$(GREEN)Running integration tests...$(NC)"
	$(PYTEST) tests/integration/ -v -m integration

test-security: ## Ejecutar tests de seguridad
	@echo "$(GREEN)Running security tests...$(NC)"
	$(PYTEST) tests/security/ -v -m security

test-performance: ## Ejecutar tests de rendimiento
	@echo "$(GREEN)Running performance tests...$(NC)"
	$(PYTEST) tests/performance/ -v -m benchmark --benchmark-only

test-webdriver: ## Tests que requieren WebDriver
	@echo "$(GREEN)Running WebDriver tests...$(NC)"
	$(PYTEST) tests/ -v -m webdriver

coverage: ## Generar reporte de cobertura
	@echo "$(GREEN)Generating coverage report...$(NC)"
	$(PYTEST) tests/ --cov=. --cov-report=html --cov-report=term-missing
	@echo "$(YELLOW)Coverage report: htmlcov/index.html$(NC)"

# ===== CALIDAD DE CÓDIGO =====
lint: ## Ejecutar linters
	@echo "$(GREEN)Running linters...$(NC)"
	flake8 . --count --statistics
	pylint --rcfile=.pylintrc *.py

format: ## Formatear código (si usas black)
	@echo "$(GREEN)Formatting code...$(NC)"
	black --line-length 120 .
	isort .

security-check: ## Verificación completa de seguridad
	@echo "$(GREEN)Running comprehensive security check...$(NC)"
	bash scripts/security-check.sh

bandit: ## Análisis de seguridad con Bandit
	@echo "$(GREEN)Running Bandit security scan...$(NC)"
	bandit -r . -f json -o security_reports/bandit-report.json
	bandit -r . -f txt

safety: ## Verificar dependencias vulnerables
	@echo "$(GREEN)Checking for vulnerable dependencies...$(NC)"
	safety check --json --output security_reports/safety-report.json
	safety check

# ===== BUILD Y DISTRIBUCIÓN =====
clean: ## Limpiar archivos temporales
	@echo "$(GREEN)Cleaning temporary files...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ htmlcov/ .coverage .pytest_cache/
	rm -rf security_reports/
	rm -rf drivers/

build: clean ## Construir paquete
	@echo "$(GREEN)Building package...$(NC)"
	$(PYTHON) -m build

install-local: build ## Instalar localmente desde build
	@echo "$(GREEN)Installing local package...$(NC)"
	$(PIP) install dist/*.whl

# ===== DOCKER =====
docker-build: ## Construir imagen Docker
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build -t $(PROJECT_NAME):latest .

docker-run: ## Ejecutar en contenedor Docker
	@echo "$(GREEN)Running in Docker container...$(NC)"
	docker run -it --rm $(PROJECT_NAME):latest

docker-test: ## Ejecutar tests en Docker
	@echo "$(GREEN)Running tests in Docker...$(NC)"
	docker run --rm $(PROJECT_NAME):latest pytest tests/

# ===== DOCUMENTACIÓN =====
docs: ## Generar documentación
	@echo "$(GREEN)Generating documentation...$(NC)"
	mkdir -p docs
	$(PYTHON) -c "import $(PROJECT_NAME); help($(PROJECT_NAME))" > docs/help.txt

docs-serve: ## Servir documentación localmente
	@echo "$(GREEN)Serving documentation...$(NC)"
	cd docs && $(PYTHON) -m http.server 8000

# ===== DESARROLLO =====
dev-server: ## Servidor de desarrollo con recarga automática
	@echo "$(GREEN)Starting development server...$(NC)"
	watchdog --patterns="*.py" --recursive --auto-restart $(PYTHON) badg3rfuzz.py

pre-commit: lint security-check test-unit ## Verificaciones pre-commit
	@echo "$(GREEN)✅ Pre-commit checks passed!$(NC)"

ci-full: install-dev lint security-check test coverage ## Pipeline completo de CI
	@echo "$(GREEN)✅ Full CI pipeline completed!$(NC)"

# ===== UTILIDADES =====
check-deps: ## Verificar dependencias actualizadas
	@echo "$(GREEN)Checking for dependency updates...$(NC)"
	$(PIP) list --outdated

upgrade-deps: ## Actualizar dependencias
	@echo "$(GREEN)Upgrading dependencies...$(NC)"
	$(PIP) install --upgrade -r requirements.txt -r requirements-dev.txt

version: ## Mostrar versión del proyecto
	@echo "$(GREEN)Project version:$(NC)"
	@$(PYTHON) -c "import $(PROJECT_NAME); print($(PROJECT_NAME).__version__)" 2>/dev/null || echo "Version not defined"

info: ## Información del sistema
	@echo "$(GREEN)System Information:$(NC)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Pip: $$($(PIP) --version)"
	@echo "OS: $$(uname -s)"
	@echo "Architecture: $$(uname -m)"
