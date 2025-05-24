import subprocess
import os
from api.utils.callback import send_callback

def run_deployment(request):
    try:
        inventory_content = f"[target]\n{request.server_ip} ansible_user={request.ssh_user} ansible_ssh_private_key_file={request.ssh_key_path}"
        with open("ansible/inventory/dynamic.ini", "w") as f:
            f.write(inventory_content)

        result = subprocess.run(
            ["ansible-playbook", "-i", "ansible/inventory/dynamic.ini", "ansible/playbooks/deploy.yml", "--extra-vars", f"image={request.container_image}"],
            capture_output=True,
            text=True
        )

        response = {
            "status": "success" if result.returncode == 0 else "failure",
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
            "server_ip": request.server_ip
        }
        send_callback(request.callback_url, response)

    except Exception as e:
        response = {"status": "failure", "error": str(e), "server_ip": request.server_ip}
        send_callback(request.callback_url, response)
    finally:
        if os.path.exists("ansible/inventory/dynamic.ini"):
            os.remove("ansible/inventory/dynamic.ini")