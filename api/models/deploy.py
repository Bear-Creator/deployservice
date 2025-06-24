"""Deployment request models."""

import os
from pathlib import Path
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, Field, ValidationInfo, field_validator

from api.models.base import DatabaseConfig


class ServerIdRequest(BaseModel):
    """Request model for server ID."""

    server_id: str = Field(
        ...,
        description=("ID сервера из /server/add"),
    )


class DeployRequest(BaseModel):
    """Request model for deploying a containerized application."""

    server_id: str = Field(
        ...,
        description=("ID сервера из /server/add"),
    )
    container_image: str
    volume_name: str
    callback_url: AnyHttpUrl
    database: Optional[DatabaseConfig] = None

    @field_validator("container_image")
    @classmethod
    def validate_container_image(cls, v: str) -> str:
        """Ensure container image is not empty and contains a tag."""
        v = v.strip()
        if not v:
            raise ValueError("Container image cannot be empty")
        if ":" not in v:
            raise ValueError("Container image must include tag (e.g., 'image:tag')")
        return v

    def get_container_name(self) -> str:
        """Extract container name from image."""
        return self.container_image.split(":")[0]


class BackupRequest(BaseModel):
    """Request model for backing up a containerized application."""

    server_id: str = Field(
        ...,
        description=("ID сервера из /server/add"),
    )
    container_name: str
    backup_image_name: str
    callback_url: AnyHttpUrl
    database: Optional[DatabaseConfig] = None

    @field_validator("container_name", "backup_image_name")
    @classmethod
    def validate_names(cls, v: str) -> str:
        """Ensure container and backup names are not empty."""
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v


class RestoreRequest(BaseModel):
    """Request model for restoring a containerized application."""

    server_id: str = Field(
        ...,
        description=("ID сервера из /server/add"),
    )
    container_name: str
    backup_image_file: str
    backup_db_file: Optional[str] = None
    volume_name: str
    callback_url: AnyHttpUrl
    database: Optional[DatabaseConfig] = None

    @field_validator("container_name")
    @classmethod
    def validate_container_name(cls, v: str) -> str:
        """Ensure container name is not empty."""
        v = v.strip()
        if not v:
            raise ValueError("Container name cannot be empty")
        return v

    @field_validator("backup_image_file", "backup_db_file")
    @classmethod
    def validate_backup_files(
        cls, v: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        """Validate backup file paths and presence if required."""
        if v is not None:
            v = v.strip()
        # Skip validation in test environment
        if os.getenv("TESTING") == "true":
            return v
        if v:
            file_path = Path(v)
            if not file_path.is_file():
                raise ValueError(f"{info.field_name} must be a valid file path")
            if not os.access(file_path, os.R_OK):
                raise ValueError(f"{info.field_name} must be readable")
        # Validate backup_db_file is provided when db_type is specified
        if info.field_name == "backup_db_file" and info.data.get("db_type") and not v:
            raise ValueError("backup_db_file is required when db_type is specified")
        return v

    def get_backup_image_name(self) -> str:
        """Extract backup image name from file path."""
        return Path(self.backup_image_file).stem


class RemoveRequest(BaseModel):
    """Request model for removing a containerized application."""

    server_id: str = Field(
        ...,
        description=("ID сервера из /server/add"),
    )
    container_name: str
    volume_name: str
    callback_url: AnyHttpUrl

    @field_validator("container_name")
    @classmethod
    def validate_container_name(cls, v: str) -> str:
        """Ensure container name is not empty."""
        v = v.strip()
        if not v:
            raise ValueError("Container name cannot be empty")
        return v


class AddServerRequest(BaseModel):
    """Request model for adding a server to inventory."""

    server_ip: str = Field(
        ...,
        description=("IP-адрес сервера"),
    )
    ssh_user: str = Field(
        ...,
        description=("Пользователь SSH"),
    )
