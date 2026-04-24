.DEFAULT_GOAL := help
SHELL := /bin/bash

MODULE ?= 01
DEMO   ?= simple-rag

.PHONY: help setup test test-module redteam demo docs lint

help:  ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

setup:  ## Instala todas las dependencias (uv sync --all-extras)
	@command -v uv >/dev/null 2>&1 || { echo "uv no encontrado. Instala desde https://docs.astral.sh/uv/"; exit 1; }
	uv sync --all-extras

test:  ## Ejecuta todos los tests del repo
	uv run pytest modules/ -v --tb=short

test-module:  ## Ejecuta tests de un módulo. Uso: make test-module MODULE=01
	uv run pytest modules/$(MODULE)*/tests/ -v --tb=short

redteam:  ## Ejecuta red team nightly (Garak + DeepTeam) — requiere setup completo
	@echo "Red team: implementar en Fase 3 (módulos 07 y 08)"

demo:  ## Levanta un demo con Docker Compose. Uso: make demo DEMO=simple-rag
	docker compose -f docker/compose.yml up $(DEMO)

docs:  ## Sirve la documentación localmente
	@command -v python3 >/dev/null && python3 -m http.server 8080 --directory docs || echo "Python3 no encontrado"

lint:  ## Lint con ruff
	uv run ruff check .
	uv run ruff format --check .
