"""Deployment service functions."""

import json
import os
import subprocess
import uuid
from typing import Any, Callable, Dict, Optional

import structlog
from fastapi import BackgroundTasks

from api.config import settings
from api.exceptions import DeploymentError
from api.models.deploy import (
    AddServerRequest,
    BackupRequest,
    DeployRequest,
    RemoveRequest,
    RestoreRequest,
)
from api.utils.ansible import ansible_manager
from api.utils.callback import send_callback

logger = structlog.get_logger(__name__)

SERVERS_JSON = settings.ansible_inventory_dir / "servers.json"


async def handle_operation(
    operation_name: str,
    request: Any,
    background_tasks: BackgroundTasks,
    server: dict,
    ansible_func: Callable[..., None],
    ansible_args: dict,
    success_message: str,
    error_message: str,
    callback_url_field: str = "callback_url",
    extra_response: Optional[dict] = None,
) -> Dict[str, Any]:
    """
    Универсальный обработчик операций с логированием, callback и ошибками.
    ansible_func — функция ansible_manager (deploy_container, backup_container и т.д.)
    ansible_args — словарь аргументов для ansible_func
    extra_response — дополнительные поля для успешного ответа
    """
    try:
        logger.info(
            f"Starting {operation_name}",
            **{k: getattr(request, k, None) for k in request.__class__.model_fields},
            server_ip=server["server_ip"],
        )
        ansible_func(**ansible_args)
        response = {
            "status": "success",
            "message": success_message,
            **({k: getattr(request, k, None) for k in request.__class__.model_fields}),
            "server_ip": server["server_ip"],
        }
        if extra_response:
            response.update(extra_response)
        background_tasks.add_task(
            send_callback,
            str(getattr(request, callback_url_field)),
            response,
        )
        logger.info(
            f"{operation_name.capitalize()} completed successfully",
            **{k: getattr(request, k, None) for k in request.__class__.model_fields},
            server_ip=server["server_ip"],
        )
        return response
    except Exception as e:
        logger.error(
            f"{operation_name.capitalize()} failed",
            **{k: getattr(request, k, None) for k in request.__class__.model_fields},
            server_ip=server["server_ip"],
            error=str(e),
        )
        error_response = {
            "status": "error",
            "message": f"{error_message}: {str(e)}",
            **({k: getattr(request, k, None) for k in request.__class__.model_fields}),
            "server_ip": server["server_ip"],
        }
        background_tasks.add_task(
            send_callback,
            str(getattr(request, callback_url_field)),
            error_response,
        )
        raise DeploymentError(f"{error_message}: {str(e)}")


async def deploy_application(
    request: DeployRequest, background_tasks: BackgroundTasks, server: dict
) -> Dict[str, Any]:
    """Deploy a containerized application."""
    db_config = request.database.model_dump() if request.database else None
    ansible_args = dict(
        server_ip=server["server_ip"],
        ssh_user=server["ssh_user"],
        container_image=request.container_image,
        volume_name=request.volume_name,
        db_config=db_config,
    )
    result: Dict[str, Any] = await handle_operation(
        operation_name="deployment",
        request=request,
        background_tasks=background_tasks,
        server=server,
        ansible_func=ansible_manager.deploy_container,
        ansible_args=ansible_args,
        success_message="Application deployed successfully",
        error_message="Deployment failed",
    )
    return result


async def backup_application(
    request: BackupRequest, background_tasks: BackgroundTasks, server: dict
) -> Dict[str, Any]:
    """Backup a containerized application."""
    db_config = request.database.model_dump() if request.database else None
    ansible_args = dict(
        server_ip=server["server_ip"],
        ssh_user=server["ssh_user"],
        container_name=request.container_name,
        backup_image_name=request.backup_image_name,
        volume_name=getattr(request, "volume_name", ""),
        db_config=db_config,
    )
    result: Dict[str, Any] = await handle_operation(
        operation_name="backup",
        request=request,
        background_tasks=background_tasks,
        server=server,
        ansible_func=ansible_manager.backup_container,
        ansible_args=ansible_args,
        success_message="Application backed up successfully",
        error_message="Backup failed",
    )
    return result


async def restore_application(
    request: RestoreRequest, background_tasks: BackgroundTasks, server: dict
) -> Dict[str, Any]:
    """Restore a containerized application."""
    db_config = request.database.model_dump() if request.database else None
    ansible_args = dict(
        server_ip=server["server_ip"],
        ssh_user=server["ssh_user"],
        container_name=request.container_name,
        backup_image_file=request.backup_image_file,
        backup_db_file=request.backup_db_file,
        volume_name=request.volume_name,
        db_config=db_config,
    )
    result: Dict[str, Any] = await handle_operation(
        operation_name="restore",
        request=request,
        background_tasks=background_tasks,
        server=server,
        ansible_func=ansible_manager.restore_container,
        ansible_args=ansible_args,
        success_message="Application restored successfully",
        error_message="Restore failed",
    )
    return result


async def remove_application(
    request: RemoveRequest, background_tasks: BackgroundTasks, server: dict
) -> Dict[str, Any]:
    """Remove a containerized application."""
    ansible_args = dict(
        server_ip=server["server_ip"],
        ssh_user=server["ssh_user"],
        container_name=request.container_name,
        volume_name=request.volume_name,
    )
    result: Dict[str, Any] = await handle_operation(
        operation_name="removal",
        request=request,
        background_tasks=background_tasks,
        server=server,
        ansible_func=ansible_manager.remove_container,
        ansible_args=ansible_args,
        success_message="Application removed successfully",
        error_message="Removal failed",
    )
    return result


def generate_server_id() -> str:
    return f"srv-{uuid.uuid4().hex[:8]}"


def save_server(server_id: str, data: dict) -> None:
    servers = {}
    if SERVERS_JSON.exists():
        with open(SERVERS_JSON, "r", encoding="utf-8") as f:
            servers = json.load(f)
    servers[server_id] = data
    with open(SERVERS_JSON, "w", encoding="utf-8") as f:
        json.dump(servers, f, ensure_ascii=False, indent=2)


def get_server(server_id: str) -> Dict[str, Any]:
    if not SERVERS_JSON.exists():
        raise ValueError(f"Server DB not found: {SERVERS_JSON}")
    with open(SERVERS_JSON, "r", encoding="utf-8") as f:
        servers: Dict[str, Any] = json.load(f)
    if server_id not in servers:
        raise ValueError(f"Server ID not found: {server_id}")
    return servers[server_id]  # type: ignore


def get_ansible_host_line(server: dict) -> str:
    return f"{server['server_ip']} ansible_user={server['ssh_user']}\n"


def add_server_to_inventory(request: AddServerRequest) -> str:
    """Настроить сервер через Ansible, затем добавить в servers.json."""
    server_id = generate_server_id()
    data = {
        "server_ip": request.server_ip,
        "ssh_user": request.ssh_user,
    }

    inventory_path = os.path.join("ansible", "inventory", "hosts.yml")
    group_header = "[target]"
    line = get_ansible_host_line(data)
    with open(inventory_path, "w", encoding="utf-8") as f:
        f.write(f"{group_header}\n{line}")

    playbook_path = os.path.join("ansible", "playbooks", "setup_server.yml")
    pubkey_env = os.environ.get("DEPLOY_PUBKEY_PATH", "key/id_ed25519.pub")
    pubkey_path = os.path.abspath(pubkey_env)
    command = [
        "ansible-playbook",
        "-i",
        inventory_path,
        playbook_path,
        "--extra-vars",
        f"deploy_pubkey_path={pubkey_path}",
    ]
    subprocess.run(command, check=True)

    save_server(server_id, data)

    return server_id
