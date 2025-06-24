.PHONY: help install develop test lint format clean run run-prod check setup

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить только основные зависимости
	pip install -e .

develop: ## Установить dev-зависимости
	pip install -e .[dev]

test: ## Запустить тесты
	pytest tests/ -v

lint: ## Линтинг кода
	flake8 api/ tests/
	mypy api/
	black --check api/ tests/
	isort --check api/ tests/

format: ## Отформатировать код
	black api/ tests/
	isort api/ tests/

clean: ## Очистить кэш и временные файлы
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

run: ## Запустить приложение в режиме разработки
	python -m api.main

run-prod: ## Запустить приложение в продакшн режиме
	uvicorn api.main:app --host 0.0.0.0 --port 8000

check: format lint test ## Проверить код (форматирование + линтинг + тесты)

setup: ## Настроить проект для разработки
	cp env.example .env
	@echo "Проект настроен! Отредактируйте .env файл под ваши нужды."