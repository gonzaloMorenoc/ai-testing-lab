.DEFAULT_GOAL := help
SHELL         := /bin/bash
MODULE        ?= 01
DEMO          ?= simple-rag
PYTHON        := uv run python
PYTEST        := uv run pytest

# ──────────────────────────────────────────────────────────────────────────────
# Ayuda
# ──────────────────────────────────────────────────────────────────────────────
.PHONY: help
help:  ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ──────────────────────────────────────────────────────────────────────────────
# Setup
# ──────────────────────────────────────────────────────────────────────────────
.PHONY: setup
setup:  ## Instala todas las dependencias (uv sync --all-extras)
	@command -v uv >/dev/null 2>&1 || { \
		echo "❌ uv no encontrado. Instala desde https://docs.astral.sh/uv/"; \
		echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		exit 1; \
	}
	uv sync --all-extras
	@echo "✅ Entorno listo. Ejecuta: make test-module MODULE=01"

.PHONY: setup-playwright
setup-playwright:  ## Instala browsers de Playwright (necesario para módulo 11)
	uv sync --extra ui
	uv run playwright install --with-deps chromium

# ──────────────────────────────────────────────────────────────────────────────
# Testing
# ──────────────────────────────────────────────────────────────────────────────
.PHONY: test
test:  ## Ejecuta todos los tests del repo (sin llamadas LLM reales)
	$(PYTEST) modules/ -m "not slow and not redteam" --record-mode=none

.PHONY: test-module
test-module:  ## Ejecuta tests de un módulo. Uso: make test-module MODULE=01
	@echo "▶ Ejecutando módulo $(MODULE)..."
	$(PYTEST) modules/$(MODULE)*/tests/ --record-mode=none -v

.PHONY: test-slow
test-slow:  ## Ejecuta tests que hacen llamadas LLM reales (requiere API keys)
	$(PYTEST) modules/ -m "slow" -v

.PHONY: test-cov
test-cov:  ## Tests con reporte de cobertura
	$(PYTEST) modules/ -m "not slow and not redteam" --record-mode=none \
		--cov=modules --cov-report=html --cov-report=term-missing

# ──────────────────────────────────────────────────────────────────────────────
# Red Team
# ──────────────────────────────────────────────────────────────────────────────
.PHONY: redteam
redteam:  ## Ejecuta red team completo (Garak + DeepTeam) — solo uso local/nightly
	@echo "⚠️  Red team puede tardar varios minutos y hace llamadas LLM reales."
	@echo "   Asegúrate de tener GROQ_API_KEY o OLLAMA corriendo."
	$(PYTEST) modules/ -m "redteam" -v

.PHONY: garak
garak:  ## Escanea el vulnerable-bot con Garak (requiere módulo 07 implementado)
	@echo "▶ Ejecutando Garak contra vulnerable-bot..."
	uv run python -m garak --target_type rest --target_name http://localhost:8002/chat \
		--probes dan.Dan_11_0,encoding,knownbadsignatures

# ──────────────────────────────────────────────────────────────────────────────
# Demos
# ──────────────────────────────────────────────────────────────────────────────
.PHONY: demo
demo:  ## Levanta un demo con Docker Compose. Uso: make demo DEMO=simple-rag
	docker compose -f docker/compose.yml up $(DEMO)

.PHONY: demo-all
demo-all:  ## Levanta todos los demos + Langfuse + Ollama
	docker compose -f docker/compose.yml up

.PHONY: demo-down
demo-down:  ## Para todos los contenedores
	docker compose -f docker/compose.yml down

.PHONY: ollama-pull
ollama-pull:  ## Descarga el modelo llama3.2 en Ollama (requerido por demos)
	ollama pull llama3.2
	ollama pull nomic-embed-text

# ──────────────────────────────────────────────────────────────────────────────
# Docs
# ──────────────────────────────────────────────────────────────────────────────
.PHONY: docs
docs:  ## Sirve la documentación en http://localhost:8080
	@echo "▶ Documentación disponible en http://localhost:8080"
	$(PYTHON) -m http.server 8080 --directory docs

# ──────────────────────────────────────────────────────────────────────────────
# Calidad de código
# ──────────────────────────────────────────────────────────────────────────────
.PHONY: lint
lint:  ## Lint con ruff
	uv run ruff check .

.PHONY: format
format:  ## Formatea código con ruff
	uv run ruff format .
	uv run ruff check --fix .

.PHONY: typecheck
typecheck:  ## Type checking con mypy
	uv run mypy modules/ --ignore-missing-imports

# ──────────────────────────────────────────────────────────────────────────────
# Cassettes (VCR)
# ──────────────────────────────────────────────────────────────────────────────
.PHONY: record-cassettes
record-cassettes:  ## Re-graba los cassettes VCR (requiere API keys reales)
	@echo "⚠️  Esto hará llamadas LLM reales. Asegúrate de tener API keys."
	$(PYTEST) modules/01-primer-eval/tests/ --record-mode=new_episodes -v

.PHONY: check-cassettes
check-cassettes:  ## Verifica que los cassettes existen y son válidos
	@find modules -name "*.yaml" -path "*/cassettes/*" | \
		while read f; do echo "✅ $$f"; done
	@count=$$(find modules -name "*.yaml" -path "*/cassettes/*" | wc -l); \
		echo "Total cassettes: $$count"
