"""Deployment service functions."""

from typing import Any, Dict
import json
import uuid

import structlog
from fastapi import BackgroundTasks

from api.exceptions import DeploymentError
from api.models.deploy import (
    BackupRequest,
    DeployRequest,
    RemoveRequest,
    RestoreRequest,
    AddServerRequest,
)
from api.utils.ansible import ansible_manager
from api.utils.callback import send_callback
from api.utils.terraform import terraform_manager
from api.config import settings

logger = structlog.get_logger(__name__)

SERVERS_JSON = settings.ansible_inventory_dir / "servers.json"


async def deploy_application(
    request: DeployRequest, background_tasks: BackgroundTasks, server: dict
) -> Dict[str, Any]:
    """Deploy a containerized application."""
    try:
        logger.info(
            "Starting deployment",
            container_image=request.container_image,
            server_ip=server["server_ip"],
        )
        db_config = request.database.dict() if request.database else None
        ansible_manager.deploy_container(
            server_ip=server["server_ip"],
            ssh_user=server["ssh_user"],
            ssh_key_path=server["ssh_key_path"],
            container_image=request.container_image,
            volume_name=request.volume_name,
            db_config=db_config,
        )
        response = {
            "status": "success",
            "message": "Application deployed successfully",
            "container_image": request.container_image,
            "server_ip": server["server_ip"],
            "volume_name": request.volume_name,
        }
        background_tasks.add_task(send_callback, str(request.callback_url), response)
        logger.info(
            "Deployment completed successfully",
            container_image=request.container_image,
            server_ip=server["server_ip"],
        )
        return response
    except Exception as e:
        logger.error(
            "Deployment failed",
            container_image=request.container_image,
            server_ip=server["server_ip"],
            error=str(e),
        )
        error_response = {
            "status": "error",
            "message": f"Deployment failed: {str(e)}",
            "container_image": request.container_image,
            "server_ip": server["server_ip"],
        }
        background_tasks.add_task(
            send_callback, str(request.callback_url), error_response
        )
        raise DeploymentError(f"Deployment failed: {str(e)}")


async def backup_application(
    request: BackupRequest, background_tasks: BackgroundTasks, server: dict
) -> Dict[str, Any]:
    """Backup a containerized application."""
    try:
        logger.info(
            "Starting backup",
            container_name=request.container_name,
            server_ip=server["server_ip"],
        )
        db_config = request.database.dict() if request.database else None
        ansible_manager.backup_container(
            server_ip=server["server_ip"],
            ssh_user=server["ssh_user"],
            ssh_key_path=server["ssh_key_path"],
            container_name=request.container_name,
            backup_image_name=request.backup_image_name,
            volume_name=getattr(request, "volume_name", ""),
            db_config=db_config,
        )
        response = {
            "status": "success",
            "message": "Application backed up successfully",
            "container_name": request.container_name,
            "backup_image_name": request.backup_image_name,
            "server_ip": server["server_ip"],
        }
        background_tasks.add_task(send_callback, str(request.callback_url), response)
        logger.info(
            "Backup completed successfully",
            container_name=request.container_name,
            backup_image_name=request.backup_image_name,
            server_ip=server["server_ip"],
        )
        return response
    except Exception as e:
        logger.error(
            "Backup failed",
            container_name=request.container_name,
            server_ip=server["server_ip"],
            error=str(e),
        )
        error_response = {
            "status": "error",
            "message": f"Backup failed: {str(e)}",
            "container_name": request.container_name,
            "server_ip": server["server_ip"],
        }
        background_tasks.add_task(
            send_callback, str(request.callback_url), error_response
        )
        raise DeploymentError(f"Backup failed: {str(e)}")


async def restore_application(
    request: RestoreRequest, background_tasks: BackgroundTasks, server: dict
) -> Dict[str, Any]:
    """Restore a containerized application."""
    try:
        logger.info(
            "Starting restore",
            container_name=request.container_name,
            server_ip=server["server_ip"],
        )
        db_config = request.database.dict() if request.database else None
        ansible_manager.restore_container(
            server_ip=server["server_ip"],
            ssh_user=server["ssh_user"],
            ssh_key_path=server["ssh_key_path"],
            container_name=request.container_name,
            backup_image_file=request.backup_image_file,
            backup_db_file=request.backup_db_file,
            volume_name=request.volume_name,
            db_config=db_config,
        )
        response = {
            "status": "success",
            "message": "Application restored successfully",
            "container_name": request.container_name,
            "backup_image_file": request.backup_image_file,
            "server_ip": server["server_ip"],
        }
        background_tasks.add_task(send_callback, str(request.callback_url), response)
        logger.info(
            "Restore completed successfully",
            container_name=request.container_name,
            backup_image_file=request.backup_image_file,
            server_ip=server["server_ip"],
        )
        return response
    except Exception as e:
        logger.error(
            "Restore failed",
            container_name=request.container_name,
            server_ip=server["server_ip"],
            error=str(e),
        )
        error_response = {
            "status": "error",
            "message": f"Restore failed: {str(e)}",
            "container_name": request.container_name,
            "server_ip": server["server_ip"],
        }
        background_tasks.add_task(
            send_callback, str(request.callback_url), error_response
        )
        raise DeploymentError(f"Restore failed: {str(e)}")


async def remove_application(
    request: RemoveRequest, background_tasks: BackgroundTasks, server: dict
) -> Dict[str, Any]:
    """Remove a containerized application."""
    try:
        logger.info(
            "Starting removal",
            container_name=request.container_name,
            server_ip=server["server_ip"],
        )
        ansible_manager.remove_container(
            server_ip=server["server_ip"],
            ssh_user=server["ssh_user"],
            ssh_key_path=server["ssh_key_path"],
            container_name=request.container_name,
            volume_name=request.volume_name,
        )
        response = {
            "status": "success",
            "message": "Application removed successfully",
            "container_name": request.container_name,
            "server_ip": server["server_ip"],
        }
        background_tasks.add_task(send_callback, str(request.callback_url), response)
        logger.info(
            "Removal completed successfully",
            container_name=request.container_name,
            server_ip=server["server_ip"],
        )
        return response
    except Exception as e:
        logger.error(
            "Removal failed",
            container_name=request.container_name,
            server_ip=server["server_ip"],
            error=str(e),
        )
        error_response = {
            "status": "error",
            "message": f"Removal failed: {str(e)}",
            "container_name": request.container_name,
            "server_ip": server["server_ip"],
        }
        background_tasks.add_task(
            send_callback, str(request.callback_url), error_response
        )
        raise DeploymentError(f"Removal failed: {str(e)}")


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

def get_server(server_id: str) -> dict:
    if not SERVERS_JSON.exists():
        raise ValueError(f"Server DB not found: {SERVERS_JSON}")
    with open(SERVERS_JSON, "r", encoding="utf-8") as f:
        servers = json.load(f)
    if server_id not in servers:
        raise ValueError(f"Server ID not found: {server_id}")
    return servers[server_id]

def get_ansible_host_line(server: dict) -> str:
    return f"{server['server_ip']} ansible_user={server['ssh_user']} ansible_ssh_private_key_file={server['ssh_key_path']}\n"

def add_server_to_inventory(request: AddServerRequest) -> str:
    """Добавляет сервер в servers.json и hosts.yml, возвращает server_id."""
    server_id = generate_server_id()
    data = {
        "server_ip": request.server_ip,
        "ssh_user": request.ssh_user,
        "ssh_key_path": request.ssh_key_path,
    }
    save_server(server_id, data)
    # Обновить hosts.yml (оставить только этот сервер)
    inventory_path = settings.ansible_inventory_dir / "hosts.yml"
    group_header = "[target]"
    line = get_ansible_host_line(data)
    with open(inventory_path, "w", encoding="utf-8") as f:
        f.write(f"{group_header}\n{line}")
    return server_id
