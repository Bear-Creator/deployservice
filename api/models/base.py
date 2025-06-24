"""Base models for the DeployService API."""

import ipaddress
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, HttpUrl, ValidationInfo, field_validator


class BaseRequest(BaseModel):
    """Base request model with common validations."""

    server_ip: str
    ssh_user: str
    ssh_key_path: str
    callback_url: HttpUrl
    volume_name: str = "app_data"

    @field_validator("server_ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Validate IP address."""
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError as e:
            raise ValueError(f"Invalid IP address: {e}")

    @field_validator("ssh_key_path")
    @classmethod
    def validate_ssh_key(cls, v: str) -> str:
        """Validate SSH key file exists and is readable."""
        # Skip validation in test environment
        if os.getenv("TESTING") == "true":
            return v

        key_path = Path(v)
        if not key_path.is_file():
            raise ValueError("SSH key path must be a valid file")
        if not os.access(key_path, os.R_OK):
            raise ValueError("SSH key file must be readable")
        return v

    @field_validator("ssh_user")
    @classmethod
    def validate_ssh_user(cls, v: str) -> str:
        """Validate SSH username."""
        if not v or not v.strip():
            raise ValueError("SSH user cannot be empty")
        return v.strip()


class DatabaseConfig(BaseModel):
    """Database configuration model."""

    db_type: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    db_name: Optional[str] = None

    @field_validator("db_type")
    @classmethod
    def validate_db_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate database type."""
        if v and v not in ["postgres", "mysql"]:
            raise ValueError("Database type must be 'postgres', 'mysql', or null")
        return v

    @field_validator("db_user", "db_password", "db_name")
    @classmethod
    def validate_db_fields(
        cls, v: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        """Validate database fields when db_type is specified."""
        if info.data.get("db_type") and not v:
            raise ValueError(f"{info.field_name} is required when db_type is specified")
        return v

    def has_database_config(self) -> bool:
        """Check if database configuration is complete."""
        return bool(self.db_type and self.db_user and self.db_password and self.db_name)
