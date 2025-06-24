"""Ansible utilities for the DeployService API."""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from api.config import settings
from api.exceptions import AnsibleError, FileOperationError

logger = structlog.get_logger(__name__)


class AnsibleManager:
    """Manager for Ansible operations."""

    def __init__(
        self, ansible_dir: Optional[Path] = None, inventory_dir: Optional[Path] = None
    ):
        self.ansible_dir = ansible_dir or settings.ansible_dir
        self.inventory_dir = inventory_dir or settings.ansible_inventory_dir
        self._validate_directories()

    def _validate_directories(self) -> None:
        """Validate Ansible directories exist."""
        if not self.ansible_dir.exists():
            raise AnsibleError(f"Ansible directory does not exist: {self.ansible_dir}")

        if not self.inventory_dir.exists():
            raise AnsibleError(
                f"Ansible inventory directory does not exist: {self.inventory_dir}"
            )

    def _create_inventory_file(self, server_ip: str) -> Path:
        """Create temporary inventory file."""
        try:
            inventory_content = f"[target]\n{server_ip}"

            # Create inventory directory if it doesn't exist
            self.inventory_dir.mkdir(parents=True, exist_ok=True)

            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".ini",
                dir=self.inventory_dir,
                delete=False,
            )

            with temp_file:
                temp_file.write(inventory_content)

            inventory_path = Path(temp_file.name)
            logger.debug(
                "Created inventory file", path=str(inventory_path), server_ip=server_ip
            )

            return inventory_path

        except Exception as e:
            logger.error("Failed to create inventory file", error=str(e))
            raise FileOperationError(f"Failed to create inventory file: {str(e)}")

    def _cleanup_inventory_file(self, inventory_path: Path) -> None:
        """Clean up temporary inventory file."""
        try:
            if inventory_path.exists():
                inventory_path.unlink()
                logger.debug("Cleaned up inventory file", path=str(inventory_path))
        except Exception as e:
            logger.warning(
                "Failed to cleanup inventory file",
                path=str(inventory_path),
                error=str(e),
            )

    def _build_extra_vars(self, variables: Dict[str, Any]) -> str:
        """Build extra vars string for Ansible command."""
        # Filter out None values and convert to string
        filtered_vars = {k: str(v) for k, v in variables.items() if v is not None}

        # Build space-separated string
        extra_vars = " ".join([f"{k}={v}" for k, v in filtered_vars.items()])

        logger.debug("Built extra vars", extra_vars=extra_vars)
        return extra_vars

    def _run_playbook(
        self,
        playbook: str,
        inventory: str,
        extra_vars: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> subprocess.CompletedProcess[str]:
        """Run Ansible playbook with error handling."""
        try:
            playbook_path = self.ansible_dir / "playbooks" / playbook
            inventory_path = self.inventory_dir / inventory

            if not playbook_path.exists():
                raise AnsibleError(f"Playbook not found: {playbook_path}")

            if not inventory_path.exists():
                raise AnsibleError(f"Inventory not found: {inventory_path}")

            # Build command
            command = [
                "ansible-playbook",
                "-i",
                str(inventory_path),
                str(playbook_path),
                "--verbose",
            ]

            # Add extra vars
            if extra_vars:
                command.extend(["--extra-vars", json.dumps(extra_vars)])

            # Add tags
            if tags:
                command.extend(["--tags", ",".join(tags)])

            logger.debug(
                "Running Ansible playbook",
                playbook=playbook,
                inventory=inventory,
                extra_vars=extra_vars,
                tags=tags,
            )

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,  # We'll handle errors manually
            )

            if result.returncode != 0:
                logger.error(
                    "Ansible playbook failed",
                    playbook=playbook,
                    returncode=result.returncode,
                    stderr=result.stderr,
                )
                raise AnsibleError(
                    f"Ansible playbook failed: {playbook}",
                    {
                        "returncode": result.returncode,
                        "stderr": result.stderr,
                        "stdout": result.stdout,
                    },
                )

            logger.info("Ansible playbook completed successfully", playbook=playbook)
            return result

        except subprocess.SubprocessError as e:
            logger.error("Ansible subprocess error", playbook=playbook, error=str(e))
            raise AnsibleError(f"Ansible subprocess error: {str(e)}")

    def deploy_container(
        self,
        server_ip: str,
        ssh_user: str,
        ssh_key_path: str,
        container_image: str,
        volume_name: str,
        db_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Deploy container using Ansible."""
        extra_vars = {
            "server_ip": server_ip,
            "ssh_user": ssh_user,
            "ssh_key_path": ssh_key_path,
            "container_image": container_image,
            "volume_name": volume_name,
        }

        if db_config:
            extra_vars.update(db_config)

        self._run_playbook(
            playbook="deploy.yml",
            inventory="hosts.yml",
            extra_vars=extra_vars,
            tags=["deploy"],
        )

    def backup_container(
        self,
        server_ip: str,
        ssh_user: str,
        ssh_key_path: str,
        container_name: str,
        backup_image_name: str,
        volume_name: str,
        db_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Backup container using Ansible."""
        extra_vars = {
            "server_ip": server_ip,
            "ssh_user": ssh_user,
            "ssh_key_path": ssh_key_path,
            "container_name": container_name,
            "backup_image_name": backup_image_name,
            "volume_name": volume_name,
        }

        if db_config:
            extra_vars.update(db_config)

        self._run_playbook(
            playbook="backup.yml",
            inventory="hosts.yml",
            extra_vars=extra_vars,
            tags=["backup"],
        )

    def restore_container(
        self,
        server_ip: str,
        ssh_user: str,
        ssh_key_path: str,
        container_name: str,
        backup_image_file: str,
        backup_db_file: Optional[str],
        volume_name: str,
        db_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Restore container using Ansible."""
        extra_vars = {
            "server_ip": server_ip,
            "ssh_user": ssh_user,
            "ssh_key_path": ssh_key_path,
            "container_name": container_name,
            "backup_image_file": backup_image_file,
            "volume_name": volume_name,
        }

        # Add backup_db_file if provided
        if backup_db_file:
            extra_vars["backup_db_file"] = backup_db_file

        if db_config:
            extra_vars.update(db_config)

        self._run_playbook(
            playbook="restore.yml",
            inventory="hosts.yml",
            extra_vars=extra_vars,
            tags=["restore"],
        )

    def remove_container(
        self,
        server_ip: str,
        ssh_user: str,
        ssh_key_path: str,
        container_name: str,
        volume_name: str,
    ) -> None:
        """Remove container using Ansible."""
        extra_vars = {
            "server_ip": server_ip,
            "ssh_user": ssh_user,
            "ssh_key_path": ssh_key_path,
            "container_name": container_name,
            "volume_name": volume_name,
        }

        self._run_playbook(
            playbook="remove.yml",
            inventory="hosts.yml",
            extra_vars=extra_vars,
            tags=["remove"],
        )

    def test_connection(self, server_ip: str, ssh_user: str, ssh_key_path: str) -> bool:
        """Test SSH connection to server."""
        try:
            extra_vars = {
                "server_ip": server_ip,
                "ssh_user": ssh_user,
                "ssh_key_path": ssh_key_path,
            }

            self._run_playbook(
                playbook="test_connection.yml",
                inventory="hosts.yml",
                extra_vars=extra_vars,
                tags=["test"],
            )

            logger.info("SSH connection test successful", server_ip=server_ip)
            return True

        except AnsibleError as e:
            logger.warning(
                "SSH connection test failed", server_ip=server_ip, error=str(e)
            )
            return False


# Global Ansible manager instance
ansible_manager = AnsibleManager()
