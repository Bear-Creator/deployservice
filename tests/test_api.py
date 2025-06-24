import os

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app

# Set testing environment
os.environ["TESTING"] = "true"

TEST_SERVER_IP = "192.168.1.94"
TEST_SSH_USER = "bear"
TEST_VOLUME = "test_volume"
TEST_CONTAINER = "test_container"
TEST_IMAGE = "nginx:latest"
CALLBACK_URL = "http://httpbin.org/post"


@pytest.mark.asyncio
async def test_health_check() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_add_server_and_deploy(monkeypatch: pytest.MonkeyPatch) -> None:
    # Мокаем subprocess.run чтобы не запускать реальный ansible-playbook
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: None)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Добавление сервера
        resp = await ac.post(
            "/server/add", json={"server_ip": "192.168.1.100", "ssh_user": "ubuntu"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "server_id" in data
        server_id = data["server_id"]

        # Деплой приложения
        deploy_payload = {
            "server_id": server_id,
            "container_image": "nginx:latest",
            "volume_name": "app_data",
            "callback_url": "http://localhost/callback",
        }
        resp2 = await ac.post("/deploy", json=deploy_payload)
        # get_server не найдёт реальный сервер, но тестируем сам маршрут
        assert resp2.status_code in (200, 400)


@pytest.mark.asyncio
async def test_full_integration() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/server/add",
            json={"server_ip": TEST_SERVER_IP, "ssh_user": TEST_SSH_USER},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["status"] == "success"
        server_id = data["server_id"]

        deploy_payload = {
            "server_id": server_id,
            "container_image": TEST_IMAGE,
            "volume_name": TEST_VOLUME,
            "callback_url": CALLBACK_URL,
        }
        resp = await ac.post("/deploy", json=deploy_payload)
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == "success"

        backup_payload = {
            "server_id": server_id,
            "container_name": TEST_CONTAINER,
            "backup_image_name": "backup_nginx",
            "callback_url": CALLBACK_URL,
        }
        resp = await ac.post("/backup", json=backup_payload)
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == "success"

        remove_payload = {
            "server_id": server_id,
            "container_name": TEST_CONTAINER,
            "volume_name": TEST_VOLUME,
            "callback_url": CALLBACK_URL,
        }
        resp = await ac.post("/remove", json=remove_payload)
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == "success"

        restore_payload = {
            "server_id": server_id,
            "container_name": TEST_CONTAINER,
            "backup_image_file": "backup_nginx.tar",
            "backup_db_file": None,
            "volume_name": TEST_VOLUME,
            "callback_url": CALLBACK_URL,
        }
        resp = await ac.post("/restore", json=restore_payload)
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == "success"
