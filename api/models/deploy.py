from pydantic import BaseModel

class DeployRequest(BaseModel):
    server_ip: str
    ssh_user: str
    ssh_key_path: str
    container_image: str
    callback_url: str