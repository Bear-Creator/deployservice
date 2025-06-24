# DeployService API

Современный асинхронный API для развертывания, резервного копирования, восстановления и удаления контейнеризированных приложений с использованием Terraform, Ansible и Podman.

## Возможности

- **Автоматическое развертывание** контейнеризированных приложений на удалённых серверах
- **Резервное копирование** контейнеров и баз данных (PostgreSQL, MySQL)
- **Восстановление** приложений и БД из резервных копий
- **Удаление** приложений и связанных ресурсов
- **Callback-уведомления** о завершении операций
- **Асинхронные фоновые задачи** (FastAPI BackgroundTasks)
- **Структурированное логирование** (structlog)
- **Работа с inventory через API** (добавление серверов)
- **Валидация входных данных** (Pydantic)

## 🛠 Технологии

- **FastAPI** — современный асинхронный веб-фреймворк
- **Pydantic** — строгая валидация и сериализация данных
- **Terraform** — управление инфраструктурой
- **Ansible** — автоматизация развертывания и управления
- **Podman** — контейнеризация
- **Structlog** — структурированное логирование
- **aiohttp** — асинхронные HTTP-запросы для callback

## Требования

- Python 3.8+
- Terraform
- Ansible
- Podman (на целевых серверах)

## Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd DeployService
```

### 2. Создание виртуального окружения

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей

```bash
pip install -e .
# Для разработки:
pip install -e ".[dev]"
# или через Makefile:
make dev
```

### 4. Настройка окружения

Скопируйте пример конфигурации:

```bash
cp env.example .env
```

Отредактируйте `.env` под ваши нужды (см. описание переменных в env.example).

## Запуск

### В режиме разработки

```bash
make run
# или
python -m api.main
```

### В продакшн-режиме

```bash
make run-prod
# или
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Основные команды Makefile

- `make dev` — установка dev-зависимостей
- `make run` — запуск в dev-режиме
- `make run-prod` — запуск в продакшн-режиме
- `make test` — запуск тестов
- `make lint` — линтинг (flake8, mypy)
- `make format` — автоформатирование (black, isort)
- `make check` — форматирование, линтинг и тесты
- `make clean` — очистка временных файлов

## API Endpoints (примеры)

### POST /deploy

```json
{
  "server_ip": "192.168.1.100",
  "ssh_user": "ubuntu",
  "ssh_key_path": "/path/to/key.pem",
  "container_image": "nginx:latest",
  "callback_url": "http://example.com/callback",
  "volume_name": "app_data",
  "db_type": "postgres",
  "db_user": "postgres",
  "db_password": "password",
  "db_name": "app_db"
}
```

### POST /backup

```json
{
  "server_ip": "192.168.1.100",
  "ssh_user": "ubuntu",
  "ssh_key_path": "/path/to/key.pem",
  "container_name": "my-app",
  "backup_image_name": "my-app-backup",
  "callback_url": "http://example.com/callback",
  "volume_name": "app_data",
  "db_type": "postgres",
  "db_user": "postgres",
  "db_password": "password",
  "db_name": "app_db"
}
```

### POST /restore

```json
{
  "server_ip": "192.168.1.100",
  "ssh_user": "ubuntu",
  "ssh_key_path": "/path/to/key.pem",
  "container_name": "my-app",
  "backup_image_file": "backups/my-app-backup.tar",
  "callback_url": "http://example.com/callback",
  "volume_name": "app_data",
  "db_type": "postgres",
  "db_user": "postgres",
  "db_password": "password",
  "db_name": "app_db",
  "backup_db_file": "backups/app_db.sql"
}
```

### POST /remove

```json
{
  "server_ip": "192.168.1.100",
  "ssh_user": "ubuntu",
  "ssh_key_path": "/path/to/key.pem",
  "container_name": "my-app",
  "callback_url": "http://example.com/callback",
  "volume_name": "app_data"
}
```

### POST /add-server

```json
{
  "server_ip": "192.168.1.100",
  "ssh_user": "ubuntu",
  "ssh_key_path": "/path/to/key.pem"
}
```

## Тестирование и разработка

- Запуск тестов: `make test` или `pytest`
- Проверка типов: `make lint` или `mypy api/`
- Форматирование: `make format` или `black api/ tests/ && isort api/ tests/`
- Линтинг: `flake8 api/ tests/`

## Структура проекта

```
DeployService/
├── api/
│   ├── main.py              # FastAPI приложение
│   ├── config.py            # Конфигурация
│   ├── exceptions.py        # Кастомные исключения
│   ├── models/              # Pydantic-модели
│   ├── services/            # Бизнес-логика (развертывание и др.)
│   └── utils/               # Утилиты (Ansible, Terraform, callback, логгер)
├── ansible/
│   ├── playbooks/           # Ansible плейбуки (deploy, backup, restore, remove)
│   └── roles/               # Ansible роли
├── terraform/               # Terraform конфигурации
├── tests/                   # Тесты
├── requirements.txt         # Зависимости
├── pyproject.toml           # Конфигурация проекта
├── env.example              # Пример .env
└── README.md                # Документация
```

## Конфигурация

- Все переменные окружения настраиваются через `.env` (см. `env.example`)
- Ключевые параметры: пути к директориям, настройки логирования, callback, разрешённые хосты

## Логирование

- Используется `structlog` для структурированных логов
- Управление уровнем и форматом логирования через переменные окружения (`LOG_LEVEL`, `LOG_FORMAT`)

## Безопасность

- Валидация всех входных данных (IP, SSH-ключи, логика Pydantic)
- Безопасная работа с файлами и ключами
- Обработка ошибок без утечки чувствительной информации

---

**DeployService** — быстрый и безопасный способ автоматизировать работу с контейнерами и инфраструктурой.