# DeployService API

Современный асинхронный API для автоматизированного развертывания, резервного копирования, восстановления и удаления контейнеризированных приложений с помощью Ansible, Podman и Terraform.

## Возможности

- **Автоматическое развертывание** контейнеров на новых и существующих серверах
- **Резервное копирование** контейнеров и баз данных (PostgreSQL, MySQL)
- **Восстановление** приложений и БД из резервных копий
- **Удаление** приложений и связанных ресурсов
- **Callback-уведомления** о завершении операций
- **Асинхронные фоновые задачи** (FastAPI BackgroundTasks)
- **Структурированное логирование** (structlog)
- **Работа с inventory через API** (добавление серверов)
- **Валидация входных данных** (Pydantic)
- **Полная автоматизация подготовки серверов** (установка Python, Podman, настройка sudo, добавление ключа)
- **Устойчивость к повторным запускам и ошибкам** (Ansible playbooks)
- **Интеграционные и unit-тесты**

## Технологии

- **FastAPI** — асинхронный веб-фреймворк
- **Pydantic** — строгая валидация данных
- **Ansible** — автоматизация развертывания и управления
- **Podman** — контейнеризация
- **Terraform** — управление инфраструктурой
- **Structlog** — структурированное логирование
- **pytest, httpx** — тестирование

## Требования

- Python 3.8+
- Ansible
- Terraform
- Podman (на целевых серверах)

## Установка и запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd DeployService
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Установите зависимости:**
   ```bash
   pip install -e .
   # Для разработки:
   pip install -e ".[dev]"
   # или через Makefile:
   make dev
   ```

4. **Скопируйте и настройте переменные окружения:**
   ```bash
   cp env.example .env
   # Отредактируйте .env под ваши нужды
   ```

5. **Запуск:**
   - В режиме разработки:
     ```bash
     make run
     # или
     python -m api.main
     ```
   - В продакшн-режиме:
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

**Внимание!** Поддержка приватных ключей (`ssh_key_path`) полностью удалена. Теперь серверы добавляются только по IP и пользователю. Все операции требуют `server_id`, получаемый после добавления сервера.

### POST /server/add

Добавить сервер в inventory и автоматически подготовить его (установка Python, Podman, настройка sudo, добавление публичного ключа):

```json
{
  "server_ip": "192.168.1.100",
  "ssh_user": "ubuntu"
}
```
Ответ:
```json
{
  "status": "success",
  "server_id": "..."
}
```

### POST /deploy

```json
{
  "server_id": "string",
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
  "server_id": "string",
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
  "server_id": "string",
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
  "server_id": "string",
  "container_name": "my-app",
  "callback_url": "http://example.com/callback",
  "volume_name": "app_data"
}
```

### GET /health

Проверка статуса API.

## Тестирование

- Unit- и интеграционные тесты: `make test` или `pytest`
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
│   ├── ansible.cfg          # Конфиг Ansible (roles_path, SSH)
│   ├── playbooks/           # Ansible плейбуки (deploy, backup, restore, remove, setup_server)
│   └── roles/               # Ansible роли (podman и др.)
├── terraform/               # Terraform конфигурации
├── tests/                   # Тесты (unit, интеграционные)
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

- Валидация всех входных данных (IP, логика Pydantic)
- Безопасная работа с файлами и ключами
- Обработка ошибок без утечки чувствительной информации

## Ansible и автоматизация

- **ansible.cfg**: прописан roles_path, отключена проверка SSH-ключей
- **setup_server.yml**: автоматическая подготовка нового сервера (Python, Podman, sudo, ключ)
- **playbooks** устойчивы к повторным запускам, ошибкам создания volume/контейнера, отсутствию переменных
- **registries.conf** для Podman настраивается автоматически
- Скрипты для добавления публичного ключа и настройки sudo

