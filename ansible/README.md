# Ansible для DeployService

## Структура
- `playbooks/` — основные сценарии (deploy, backup, restore, remove, setup_server)
- `roles/podman/` — роль для управления Podman и контейнерами
- `group_vars/all.yml` — общие переменные для всех playbook
- `inventory.ini` — инвентарь (определите свои хосты)

## Быстрый старт
1. Укажите свои хосты в `inventory.ini` (пример):
   ```
   [target]
   192.168.1.100 ansible_user=deploy
   ```
2. Проверьте/измените переменные в `group_vars/all.yml`.
3. Запустите нужный playbook, например:
   ```bash
   ansible-playbook -i inventory.ini playbooks/deploy.yml
   ```

## Описание playbook
- `deploy.yml` — деплой приложения/БД
- `backup.yml` — создание бэкапа контейнера и БД
- `restore.yml` — восстановление из бэкапа
- `remove.yml` — удаление контейнера и volume
- `setup_server.yml` — подготовка сервера (Python, Podman, ключи)

## Требования
- Ansible >= 2.9
- Доступ по SSH к целевым серверам 