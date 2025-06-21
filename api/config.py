"""Configuration settings for the DeployService API."""

from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application settings
    app_name: str = "DeployService API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "json"

    # Directory settings
    terraform_dir: Path = Field(default=Path("terraform"))
    ansible_dir: Path = Field(default=Path("ansible"))
    ansible_inventory_dir: Path = Field(default=Path("ansible/inventory"))
    backup_dir: Path = Field(default=Path("backups"))

    # Callback settings
    callback_timeout: int = 30
    callback_retries: int = 3

    # CORS settings
    allowed_hosts: List[str] = Field(default=["*"])

    @field_validator(
        "terraform_dir", "ansible_dir", "ansible_inventory_dir", "backup_dir"
    )
    @classmethod
    def validate_directories(cls, v: Path) -> Path:
        """Validate and create directories if they don't exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
