import subprocess
import os
import tempfile
import json
from api.utils.callback import send_callback

def get_terraform_output():
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd="terraform",
            capture_output=True,
            text=True,
            check=True
        )
        outputs = json.loads(result.stdout)
        return outputs.get("vm_public_ip", {}).get("value")
    except Exception as e:
        raise Exception(f"Failed to get Terraform outputs: {str(e)}")

def run_deployment(request):
    try:
        server_ip = get_terraform_output() if not request.server_ip else request.server_ip
        inventory_content = f"[target]\n{server_ip}"
        with open("ansible/inventory/dynamic.ini", "w") as f:
            f.write(inventory_content)

        extra_vars = (
            f"image={request.container_image} ansible_user={request.ssh_user} "
            f"volume_name={request.volume_name} container_name={request.container_image.split(':')[0]} "
            f"db_type={request.db_type or ''} db_user={request.db_user or ''} "
            f"db_password={request.db_password or ''} db_name={request.db_name or ''}"
        )
        result = subprocess.run(
            [
                "ansible-playbook",
                "-i", "ansible/inventory/dynamic.ini",
                "ansible/playbooks/deploy.yml",
                "--extra-vars", extra_vars,
                "--private-key", request.ssh_key_path
            ],
            capture_output=True,
            text=True
        )

        response = {
            "status": "success" if result.returncode == 0 else "failure",
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
            "server_ip": server_ip
        }
        send_callback(request.callback_url, response)

    except Exception as e:
        response = {"status": "failure", "error": str(e), "server_ip": request.server_ip}
        send_callback(request.callback_url, response)
    finally:
        if os.path.exists("ansible/inventory/dynamic.ini"):
            os.remove("ansible/inventory/dynamic.ini")

def run_backup(request):
    try:
        server_ip = get_terraform_output() if not request.server_ip else request.server_ip
        inventory_content = f"[target]\n{server_ip}"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as temp_file:
            temp_file.write(inventory_content)
            temp_inventory_path = temp_file.name

        extra_vars = (
            f"container_name={request.container_name} backup_image_name={request.backup_image_name} "
            f"ansible_user={request.ssh_user} volume_name={request.volume_name} "
            f"db_type={request.db_type or ''} db_user={request.db_user or ''} "
            f"db_password={request.db_password or ''} db_name={request.db_name or ''}"
        )
        result = subprocess.run(
            [
                "ansible-playbook",
                "-i", temp_inventory_path,
                "ansible/playbooks/backup.yml",
                "--extra-vars", extra_vars,
                "--private-key", request.ssh_key_path
            ],
            capture_output=True,
            text=True
        )

        response = {
            "status": "success" if result.returncode == 0 else "failure",
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
            "server_ip": server_ip,
            "backup_image_file": f"backups/{request.backup_image_name}-{result.start_time.isoformat()}.tar" if result.returncode == 0 else None,
            "backup_db_file": f"backups/{request.db_name}-{result.start_time.isoformat()}.sql" if result.returncode == 0 and request.db_type else None
        }
        send_callback(request.callback_url, response)

    except Exception as e:
        response = {"status": "failure", "error": str(e), "server_ip": request.server_ip}
        send_callback(request.callback_url, response)
    finally:
        if os.path.exists(temp_inventory_path):
            os.remove(temp_inventory_path)

def run_restore(request):
    try:
        server_ip = get_terraform_output() if not request.server_ip else request.server_ip
        inventory_content = f"[target]\n{server_ip}"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as temp_file:
            temp_file.write(inventory_content)
            temp_inventory_path = temp_file.name

        backup_image_name = os.path.basename(request.backup_image_file).split('-')[0]
        extra_vars = (
            f"container_name={request.container_name} backup_image_file={request.backup_image_file} "
            f"backup_image_name={backup_image_name} ansible_user={request.ssh_user} "
            f"volume_name={request.volume_name} db_type={request.db_type or ''} "
            f"db_user={request.db_user or ''} db_password={request.db_password or ''} "
            f"db_name={request.db_name or ''} backup_db_file={request.backup_db_file or ''}"
        )
        result = subprocess.run(
            [
                "ansible-playbook",
                "-i", temp_inventory_path,
                "ansible/playbooks/restore.yml",
                "--extra-vars", extra_vars,
                "--private-key", request.ssh_key_path
            ],
            capture_output=True,
            text=True
        )

        response = {
            "status": "success" if result.returncode == 0 else "failure",
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
            "server_ip": server_ip
        }
        send_callback(request.callback_url, response)

    except Exception as e:
        response = {"status": "failure", "error": str(e), "server_ip": request.server_ip}
        send_callback(request.callback_url, response)
    finally:
        if os.path.exists(temp_inventory_path):
            os.remove(temp_inventory_path)

def run_remove(request):
    try:
        server_ip = get_terraform_output() if not request.server_ip else request.server_ip
        inventory_content = f"[target]\n{server_ip}"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as temp_file:
            temp_file.write(inventory_content)
            temp_inventory_path = temp_file.name

        extra_vars = f"container_name={request.container_name} ansible_user={request.ssh_user} volume_name={request.volume_name}"
        result = subprocess.run(
            [
                "ansible-playbook",
                "-i", temp_inventory_path,
                "ansible/playbooks/remove.yml",
                "--extra-vars", extra_vars,
                "--private-key", request.ssh_key_path
            ],
            capture_output=True,
            text=True
        )

        response = {
            "status": "success" if result.returncode == 0 else "failure",
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
            "server_ip": server_ip
        }
        send_callback(request.callback_url, response)

    except Exception as e:
        response = {"status": "failure", "error": str(e), "server_ip": request.server_ip}
        send_callback(request.callback_url, response)
    finally:
        if os.path.exists(temp_inventory_path):
            os.remove(temp_inventory_path)