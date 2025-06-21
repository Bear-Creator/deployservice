"""Tests for data models."""

import pytest
from pydantic import ValidationError

from api.models.deploy import (
    DeployRequest,
    BackupRequest,
    RestoreRequest,
    RemoveRequest,
)


class TestDeployRequest:
    """Test DeployRequest model."""

    def test_valid_deploy_request(self):
        """Test valid deployment request."""
        request = DeployRequest(
            server_ip="192.168.1.100",
            ssh_user="ubuntu",
            ssh_key_path="tests/fixtures/test_key.pem",
            container_image="nginx:latest",
            callback_url="http://example.com/callback",
        )

        assert request.server_ip == "192.168.1.100"
        assert request.ssh_user == "ubuntu"
        assert request.container_image == "nginx:latest"
        assert request.get_container_name() == "nginx"

    def test_invalid_ip_address(self):
        """Test invalid IP address."""
        with pytest.raises(ValidationError, match="Invalid IP address"):
            DeployRequest(
                server_ip="invalid-ip",
                ssh_user="ubuntu",
                ssh_key_path="tests/fixtures/test_key.pem",
                container_image="nginx:latest",
                callback_url="http://example.com/callback",
            )

    def test_invalid_container_image(self):
        """Test invalid container image format."""
        with pytest.raises(ValidationError, match="Container image must include tag"):
            DeployRequest(
                server_ip="192.168.1.100",
                ssh_user="ubuntu",
                ssh_key_path="tests/fixtures/test_key.pem",
                container_image="nginx",
                callback_url="http://example.com/callback",
            )

    def test_database_config(self):
        """Test database configuration."""
        request = DeployRequest(
            server_ip="192.168.1.100",
            ssh_user="ubuntu",
            ssh_key_path="tests/fixtures/test_key.pem",
            container_image="nginx:latest",
            callback_url="http://example.com/callback",
            db_type="postgres",
            db_user="postgres",
            db_password="password",
            db_name="app_db",
        )

        assert request.has_database_config() is True
        assert request.db_type == "postgres"
        assert request.db_user == "postgres"

    def test_invalid_db_type(self):
        """Test invalid database type."""
        with pytest.raises(ValidationError, match="Database type must be"):
            DeployRequest(
                server_ip="192.168.1.100",
                ssh_user="ubuntu",
                ssh_key_path="tests/fixtures/test_key.pem",
                container_image="nginx:latest",
                callback_url="http://example.com/callback",
                db_type="invalid_db",
            )


class TestBackupRequest:
    """Test BackupRequest model."""

    def test_valid_backup_request(self):
        """Test valid backup request."""
        request = BackupRequest(
            server_ip="192.168.1.100",
            ssh_user="ubuntu",
            ssh_key_path="tests/fixtures/test_key.pem",
            container_name="my-app",
            backup_image_name="my-app-backup",
            callback_url="http://example.com/callback",
        )

        assert request.server_ip == "192.168.1.100"
        assert request.container_name == "my-app"
        assert request.backup_image_name == "my-app-backup"

    def test_empty_container_name(self):
        """Test empty container name."""
        with pytest.raises(ValidationError, match="Name cannot be empty"):
            BackupRequest(
                server_ip="192.168.1.100",
                ssh_user="ubuntu",
                ssh_key_path="tests/fixtures/test_key.pem",
                container_name="",
                backup_image_name="my-app-backup",
                callback_url="http://example.com/callback",
            )


class TestRestoreRequest:
    """Test RestoreRequest model."""

    def test_valid_restore_request(self):
        """Test valid restore request."""
        request = RestoreRequest(
            server_ip="192.168.1.100",
            ssh_user="ubuntu",
            ssh_key_path="tests/fixtures/test_key.pem",
            container_name="my-app",
            backup_image_file="backups/my-app-backup.tar",
            callback_url="http://example.com/callback",
        )

        assert request.server_ip == "192.168.1.100"
        assert request.container_name == "my-app"
        assert request.backup_image_file == "backups/my-app-backup.tar"
        assert request.get_backup_image_name() == "my-app-backup"

    def test_restore_with_database(self):
        """Test restore request with database backup."""
        request = RestoreRequest(
            server_ip="192.168.1.100",
            ssh_user="ubuntu",
            ssh_key_path="tests/fixtures/test_key.pem",
            container_name="my-app",
            backup_image_file="backups/my-app-backup.tar",
            callback_url="http://example.com/callback",
            db_type="postgres",
            db_user="postgres",
            db_password="password",
            db_name="app_db",
            backup_db_file="backups/app_db.sql",
        )

        assert request.has_database_config() is True
        assert request.backup_db_file == "backups/app_db.sql"


class TestRemoveRequest:
    """Test RemoveRequest model."""

    def test_valid_remove_request(self):
        """Test valid remove request."""
        request = RemoveRequest(
            server_ip="192.168.1.100",
            ssh_user="ubuntu",
            ssh_key_path="tests/fixtures/test_key.pem",
            container_name="my-app",
            callback_url="http://example.com/callback",
        )

        assert request.server_ip == "192.168.1.100"
        assert request.container_name == "my-app"

    def test_empty_container_name(self):
        """Test empty container name."""
        with pytest.raises(ValidationError, match="Container name cannot be empty"):
            RemoveRequest(
                server_ip="192.168.1.100",
                ssh_user="ubuntu",
                ssh_key_path="tests/fixtures/test_key.pem",
                container_name="",
                callback_url="http://example.com/callback",
            )
