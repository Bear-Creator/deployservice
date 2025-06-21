"""Main FastAPI application."""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

import structlog
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import settings
from api.exceptions import DeployServiceError
from api.models.deploy import (
    BackupRequest,
    DeployRequest,
    RemoveRequest,
    RestoreRequest,
    AddServerRequest,
)
from api.services.deployment import (
    backup_application,
    deploy_application,
    remove_application,
    restore_application,
    add_server_to_inventory,
    get_server,
    get_ansible_host_line,
    save_server,
)
from api.utils.logger import configure_logging

# Configure logging
configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting DeployService API")

    # Startup tasks
    logger.info("DeployService API started successfully")

    yield

    # Shutdown tasks
    logger.info("Shutting down DeployService API")


# Create FastAPI app
app = FastAPI(
    title="DeployService API",
    description=(
        "API for deploying, backing up, restoring, and removing "
        "containerized applications"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DeployServiceError)
async def deploy_service_exception_handler(
    request: Any, exc: DeployServiceError
) -> JSONResponse:
    """Handle DeployService exceptions."""
    logger.error("DeployService error", error=str(exc), details=exc.details)

    return JSONResponse(
        status_code=400,
        content={
            "error": "DeployService Error",
            "message": str(exc),
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Any, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error("Unexpected error", error=str(exc), exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
        },
    )


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "DeployService API"}


@app.post("/deploy")
async def deploy(
    request: DeployRequest, background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Deploy a containerized application."""
    logger.info("Deploy request received", container_image=request.container_image)

    try:
        server = get_server(request.server_id)
        inventory_path = settings.ansible_inventory_dir / "hosts.yml"
        with open(inventory_path, "w", encoding="utf-8") as f:
            f.write(f"[target]\n{get_ansible_host_line(server)}")
        result = await deploy_application(request, background_tasks, server)
        return result
    except Exception as e:
        logger.error("Deploy request failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/backup")
async def backup(
    request: BackupRequest, background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Backup a containerized application."""
    logger.info("Backup request received", container_name=request.container_name)

    try:
        server = get_server(request.server_id)
        inventory_path = settings.ansible_inventory_dir / "hosts.yml"
        with open(inventory_path, "w", encoding="utf-8") as f:
            f.write(f"[target]\n{get_ansible_host_line(server)}")
        result = await backup_application(request, background_tasks, server)
        return result
    except Exception as e:
        logger.error("Backup request failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/restore")
async def restore(
    request: RestoreRequest, background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Restore a containerized application."""
    logger.info("Restore request received", container_name=request.container_name)

    try:
        server = get_server(request.server_id)
        inventory_path = settings.ansible_inventory_dir / "hosts.yml"
        with open(inventory_path, "w", encoding="utf-8") as f:
            f.write(f"[target]\n{get_ansible_host_line(server)}")
        result = await restore_application(request, background_tasks, server)
        return result
    except Exception as e:
        logger.error("Restore request failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/remove")
async def remove(
    request: RemoveRequest, background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Remove a containerized application."""
    logger.info("Remove request received", container_name=request.container_name)

    try:
        server = get_server(request.server_id)
        inventory_path = settings.ansible_inventory_dir / "hosts.yml"
        with open(inventory_path, "w", encoding="utf-8") as f:
            f.write(f"[target]\n{get_ansible_host_line(server)}")
        result = await remove_application(request, background_tasks, server)
        return result
    except Exception as e:
        logger.error("Remove request failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/server/add")
async def add_server(request: AddServerRequest) -> dict:
    """Добавить сервер в Ansible inventory и получить server_id."""
    server_id = add_server_to_inventory(request)
    logger.info("Server added to inventory", server_ip=request.server_ip, server_id=server_id)
    return {"status": "success", "server_id": server_id}
