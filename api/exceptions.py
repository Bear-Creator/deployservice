"""Custom exceptions for the DeployService API."""

from typing import Any, Dict, Optional


class DeployServiceError(Exception):
    """Base exception for DeployService."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DeploymentError(DeployServiceError):
    """Exception raised when deployment operations fail."""

    pass


class TerraformError(DeployServiceError):
    """Exception raised when Terraform operations fail."""

    pass


class AnsibleError(DeployServiceError):
    """Exception raised when Ansible operations fail."""

    pass


class ValidationError(DeployServiceError):
    """Exception raised when request validation fails."""

    pass


class CallbackError(DeployServiceError):
    """Exception raised when callback operations fail."""

    pass


class FileOperationError(DeployServiceError):
    """Exception raised when file operations fail."""

    pass


class SSHConnectionError(DeployServiceError):
    """Exception raised when SSH connection fails."""

    pass


class ContainerOperationError(DeployServiceError):
    """Exception raised when container operations fail."""

    pass


class DatabaseOperationError(DeployServiceError):
    """Exception raised when database operations fail."""

    pass
