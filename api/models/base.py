"""Base models for the DeployService API."""

import ipaddress
from typing import Optional

from pydantic import BaseModel, HttpUrl, ValidationInfo, field_validator


class BaseRequest(BaseModel):
    """Base request model with common validations for server and SSH user."""

    server_ip: str
    ssh_user: str
    callback_url: HttpUrl
    volume_name: str = "app_data"

    @field_validator("server_ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Validate that the value is a valid IP address."""
        v = v.strip()
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError as e:
            raise ValueError(f"Invalid IP address: {e}")

    @field_validator("ssh_user")
    @classmethod
    def validate_ssh_user(cls, v: str) -> str:
        """Validate that SSH username is not empty."""
        v = v.strip()
        if not v:
            raise ValueError("SSH user cannot be empty")
        return v


class DatabaseConfig(BaseModel):
    """Database configuration model for containerized applications."""

    db_type: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    db_name: Optional[str] = None

    @field_validator("db_type")
    @classmethod
    def validate_db_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate that db_type is either 'postgres', 'mysql', or None."""
        if v is not None:
            v = v.strip()
        if v and v not in ["postgres", "mysql"]:
            raise ValueError("Database type must be 'postgres', 'mysql', or null")
        return v

    @field_validator("db_user", "db_password", "db_name")
    @classmethod
    def validate_db_fields(
        cls, v: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        """Validate that DB fields are present when db_type is specified."""
        if v is not None:
            v = v.strip()
        if info.data.get("db_type") and not v:
            raise ValueError(f"{info.field_name} is required when db_type is specified")
        return v

    def has_database_config(self) -> bool:
        """Check if database configuration is complete."""
        return bool(self.db_type and self.db_user and self.db_password and self.db_name)
