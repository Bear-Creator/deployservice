# DeployService API

Современный API для развертывания, резервного копирования, восстановления и удаления контейнеризированных приложений с использованием Terraform и Ansible.

## Возможности

- **Развертывание приложений**: Автоматическое развертывание контейнеризированных приложений
- **Резервное копирование**: Создание резервных копий контейнеров и баз данных
- **Восстановление**: Восстановление приложений из резервных копий
- **Удаление**: Безопасное удаление приложений и связанных ресурсов
- **Поддержка баз данных**: PostgreSQL и MySQL
- **Асинхронные операции**: Все операции выполняются в фоновом режиме
- **Callback уведомления**: Уведомления о завершении операций
- **Структурированное логирование**: Подробные логи всех операций

## 🛠 Технологии

- **FastAPI** - современный веб-фреймворк для Python
- **Pydantic** - валидация данных и сериализация
- **Terraform** - управление инфраструктурой
- **Ansible** - автоматизация развертывания
- **Podman** - контейнеризация
- **Structlog** - структурированное логирование

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
```

### 4. Настройка окружения

Скопируйте файл конфигурации:

```bash
cp env.example .env
```

Отредактируйте `.env` файл под ваши нужды:

```env
# API Settings
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Terraform
TERRAFORM_DIR=terraform

# Ansible
ANSIBLE_DIR=ansible
ANSIBLE_INVENTORY_DIR=ansible/inventory

# Backup
BACKUP_DIR=backups

# Callback
CALLBACK_TIMEOUT=30
CALLBACK_RETRIES=3

# Security
ALLOWED_HOSTS=["*"]
```

## Запуск

### Разработка

```bash
python -m api.main
```

### Продакшн

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Развертывание приложения

```http
POST /deploy
Content-Type: application/json

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

### Резервное копирование

```http
POST /backup
Content-Type: application/json

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

### Восстановление

```http
POST /restore
Content-Type: application/json

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

### Удаление

```http
POST /remove
Content-Type: application/json

{
  "server_ip": "192.168.1.100",
  "ssh_user": "ubuntu",
  "ssh_key_path": "/path/to/key.pem",
  "container_name": "my-app",
  "callback_url": "http://example.com/callback",
  "volume_name": "app_data"
}
```

## Тестирование

### Запуск тестов

```bash
pytest
```

### Проверка типов

```bash
mypy api/
```

### Форматирование кода

```bash
black api/
isort api/
```

### Линтинг

```bash
flake8 api/
```

## Структура проекта

```
DeployService/
├── api/
│   ├── __init__.py
│   ├── main.py              # Основное приложение FastAPI
│   ├── config.py            # Конфигурация приложения
│   ├── exceptions.py        # Кастомные исключения
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py          # Базовые модели
│   │   └── deploy.py        # Модели запросов
│   ├── services/
│   │   ├── __init__.py
│   │   └── deployment.py    # Сервисы развертывания
│   └── utils/
│       ├── __init__.py
│       ├── ansible.py       # Утилиты Ansible
│       ├── callback.py      # Утилиты callback
│       ├── logger.py        # Система логирования
│       └── terraform.py     # Утилиты Terraform
├── ansible/
│   ├── playbooks/           # Ansible плейбуки
│   └── roles/               # Ansible роли
├── terraform/               # Terraform конфигурации
├── tests/                   # Тесты
├── requirements.txt         # Зависимости Python
├── pyproject.toml          # Конфигурация проекта
├── env.example             # Пример конфигурации
└── README.md               # Документация
```

## Конфигурация

### Terraform

Убедитесь, что в директории `terraform/` есть файл `main.tf` с конфигурацией инфраструктуры.

### Ansible

Убедитесь, что в директории `ansible/playbooks/` есть следующие плейбуки:
- `deploy.yml` - развертывание приложения
- `backup.yml` - создание резервной копии
- `restore.yml` - восстановление из резервной копии
- `remove.yml` - удаление приложения

## Логирование

API использует структурированное логирование с помощью `structlog`. Логи можно настроить через переменные окружения:

- `LOG_LEVEL` - уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FORMAT` - формат логов (json, console)

## Безопасность

- Валидация всех входных данных
- Безопасная работа с файлами
- Проверка SSH ключей
- Валидация IP адресов
- Обработка ошибок без утечки информации