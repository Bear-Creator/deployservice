"""Tests for data models."""

import pytest
from pydantic import ValidationError

from api.models.base import DatabaseConfig
from api.models.deploy import (
    AddServerRequest,
    BackupRequest,
    DeployRequest,
    RemoveRequest,
    RestoreRequest,
)


class TestDeployRequest:
    """Test DeployRequest model."""

    def test_valid_deploy_request(self):
        """Test valid deployment request."""
        request = DeployRequest(
            server_id="srv-123",
            container_image="nginx:latest",
            volume_name="app_data",
            callback_url="http://localhost/callback",
        )

        assert request.server_id == "srv-123"
        assert request.container_image == "nginx:latest"
        assert request.get_container_name() == "nginx"

    def test_invalid_image(self):
        """Test invalid container image format."""
        with pytest.raises(ValidationError, match="Container image must include tag"):
            DeployRequest(
                server_id="srv-123",
                container_image="nginx",
                volume_name="app_data",
                callback_url="http://localhost/callback",
            )

    def test_database_config(self):
        """Test database configuration."""
        request = DeployRequest(
            server_id="srv-123",
            container_image="nginx:latest",
            volume_name="app_data",
            callback_url="http://localhost/callback",
            database=DatabaseConfig(
                db_type="postgres",
                db_user="postgres",
                db_password="password",
                db_name="app_db",
            ),
        )
        assert request.database is not None
        assert request.database.has_database_config() is True
        assert request.database.db_type == "postgres"
        assert request.database.db_user == "postgres"

    def test_invalid_db_type(self):
        """Test invalid database type."""
        with pytest.raises(ValidationError, match="Database type must be"):
            DeployRequest(
                server_id="srv-123",
                container_image="nginx:latest",
                volume_name="app_data",
                callback_url="http://localhost/callback",
                database=DatabaseConfig(db_type="invalid_db"),
            )


class TestBackupRequest:
    """Test BackupRequest model."""

    def test_valid_backup_request(self):
        """Test valid backup request."""
        request = BackupRequest(
            server_id="srv-123",
            container_name="nginx",
            backup_image_name="nginx-backup",
            callback_url="http://localhost/callback",
        )

        assert request.container_name == "nginx"
        assert request.backup_image_name == "nginx-backup"

    def test_empty_container_name(self):
        """Test empty container name."""
        with pytest.raises(ValidationError, match="Name cannot be empty"):
            BackupRequest(
                server_id="srv-123",
                container_name="",
                backup_image_name="nginx-backup",
                callback_url="http://localhost/callback",
            )


class TestRestoreRequest:
    """Test RestoreRequest model."""

    def test_valid_restore_request(self, tmp_path):
        """Test valid restore request."""
        backup_file = tmp_path / "nginx-backup.tar"
        backup_file.write_text("fake data")
        request = RestoreRequest(
            server_id="srv-123",
            container_name="nginx",
            backup_image_file=str(backup_file),
            volume_name="app_data",
            callback_url="http://localhost/callback",
        )
        assert request.container_name == "nginx"
        assert request.backup_image_file == str(backup_file)
        assert request.get_backup_image_name() == "nginx-backup"

    def test_restore_with_database(self, tmp_path):
        """Test restore request with database backup."""
        backup_file = tmp_path / "nginx-backup.tar"
        backup_file.write_text("fake data")
        db_file = tmp_path / "app_db.sql"
        db_file.write_text("fake data")
        request = RestoreRequest(
            server_id="srv-123",
            container_name="nginx",
            backup_image_file=str(backup_file),
            volume_name="app_data",
            callback_url="http://localhost/callback",
            database=DatabaseConfig(
                db_type="postgres",
                db_user="postgres",
                db_password="password",
                db_name="app_db",
            ),
            backup_db_file=str(db_file),
        )
        assert request.database is not None
        assert request.database.has_database_config() is True
        assert request.backup_db_file == str(db_file)


class TestRemoveRequest:
    """Test RemoveRequest model."""

    def test_valid_remove_request(self):
        """Test valid remove request."""
        request = RemoveRequest(
            server_id="srv-123",
            container_name="nginx",
            volume_name="app_data",
            callback_url="http://localhost/callback",
        )

        assert request.container_name == "nginx"
        assert request.volume_name == "app_data"

    def test_empty_container_name(self):
        """Test empty container name."""
        with pytest.raises(ValidationError, match="Container name cannot be empty"):
            RemoveRequest(
                server_id="srv-123",
                container_name="",
                volume_name="app_data",
                callback_url="http://localhost/callback",
            )


def test_add_server_request():
    req = AddServerRequest(server_ip="192.168.1.100", ssh_user="ubuntu")
    assert req.server_ip == "192.168.1.100"
    assert req.ssh_user == "ubuntu"


def test_deploy_request_valid():
    req = DeployRequest(
        server_id="srv-123",
        container_image="nginx:latest",
        volume_name="app_data",
        callback_url="http://localhost/callback",
    )
    assert req.server_id == "srv-123"
    assert req.container_image == "nginx:latest"
    assert req.get_container_name() == "nginx"


def test_deploy_request_invalid_image():
    with pytest.raises(ValidationError):
        DeployRequest(
            server_id="srv-123",
            container_image="nginx",
            volume_name="app_data",
            callback_url="http://localhost/callback",
        )


def test_backup_request():
    req = BackupRequest(
        server_id="srv-123",
        container_name="nginx",
        backup_image_name="nginx-backup",
        callback_url="http://localhost/callback",
    )
    assert req.container_name == "nginx"
    assert req.backup_image_name == "nginx-backup"


def test_restore_request(tmp_path):
    backup_file = tmp_path / "nginx-backup.tar"
    backup_file.write_text("fake data")
    req = RestoreRequest(
        server_id="srv-123",
        container_name="nginx",
        backup_image_file=str(backup_file),
        volume_name="app_data",
        callback_url="http://localhost/callback",
    )
    assert req.container_name == "nginx"
    assert req.backup_image_file == str(backup_file)
    assert req.get_backup_image_name() == "nginx-backup"


def test_remove_request():
    req = RemoveRequest(
        server_id="srv-123",
        container_name="nginx",
        volume_name="app_data",
        callback_url="http://localhost/callback",
    )
    assert req.container_name == "nginx"
    assert req.volume_name == "app_data"
