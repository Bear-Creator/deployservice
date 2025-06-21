"""Terraform utilities for the DeployService API."""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from api.config import settings
from api.exceptions import TerraformError

logger = structlog.get_logger(__name__)


class TerraformManager:
    """Manager for Terraform operations."""

    def __init__(self, terraform_dir: Optional[Path] = None):
        self.terraform_dir = terraform_dir or settings.terraform_dir
        self._validate_terraform_dir()

    def _validate_terraform_dir(self) -> None:
        """Validate Terraform directory exists and contains main.tf."""
        if not self.terraform_dir.exists():
            raise TerraformError(
                f"Terraform directory does not exist: {self.terraform_dir}"
            )

        main_tf = self.terraform_dir / "main.tf"
        if not main_tf.exists():
            raise TerraformError(f"main.tf not found in Terraform directory: {main_tf}")

    def _run_command(
        self, command: List[str], capture_output: bool = True
    ) -> subprocess.CompletedProcess[str]:
        """Run Terraform command with error handling."""
        try:
            logger.debug(
                "Running Terraform command",
                command=command,
                cwd=str(self.terraform_dir),
            )

            result = subprocess.run(
                command,
                cwd=self.terraform_dir,
                capture_output=capture_output,
                text=True,
                check=False,  # We'll handle errors manually
            )

            if result.returncode != 0:
                logger.error(
                    "Terraform command failed",
                    command=command,
                    returncode=result.returncode,
                    stderr=result.stderr,
                )
                raise TerraformError(
                    f"Terraform command failed: {' '.join(command)}",
                    {
                        "returncode": result.returncode,
                        "stderr": result.stderr,
                        "stdout": result.stdout,
                    },
                )

            return result

        except subprocess.SubprocessError as e:
            logger.error("Terraform subprocess error", command=command, error=str(e))
            raise TerraformError(f"Terraform subprocess error: {str(e)}")

    def get_outputs(self) -> Dict[str, Any]:
        """Get Terraform outputs as JSON."""
        try:
            result = self._run_command(["terraform", "output", "-json"])
            outputs: Dict[str, Any] = json.loads(result.stdout)
            logger.debug("Retrieved Terraform outputs", outputs=outputs)
            return outputs
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Terraform outputs", error=str(e))
            raise TerraformError(f"Failed to parse Terraform outputs: {str(e)}")

    def get_vm_public_ip(self) -> Optional[str]:
        """Get VM public IP from Terraform outputs."""
        try:
            outputs = self.get_outputs()
            vm_ip: Optional[str] = outputs.get("vm_public_ip", {}).get("value")

            if vm_ip:
                logger.info("Retrieved VM public IP", ip=vm_ip)
            else:
                logger.warning("VM public IP not found in Terraform outputs")

            return vm_ip

        except Exception as e:
            logger.error("Failed to get VM public IP", error=str(e))
            return None

    def validate_workspace(self) -> bool:
        """Validate Terraform workspace is properly configured."""
        try:
            # Check if Terraform is initialized
            self._run_command(["terraform", "show"], capture_output=True)
            return True
        except TerraformError:
            logger.warning("Terraform workspace validation failed")
            return False

    def init_workspace(self) -> None:
        """Initialize Terraform workspace."""
        logger.info("Initializing Terraform workspace")
        self._run_command(["terraform", "init"])

    def plan_workspace(self) -> str:
        """Create Terraform plan."""
        logger.info("Creating Terraform plan")
        result = self._run_command(["terraform", "plan"])
        return result.stdout


# Global Terraform manager instance
terraform_manager = TerraformManager()
