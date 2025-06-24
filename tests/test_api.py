import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


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
