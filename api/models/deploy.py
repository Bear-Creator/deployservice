from pydantic import BaseModel, HttpUrl, validator
import os
import ipaddress

class DeployRequest(BaseModel):
    server_ip: str
    ssh_user: str
    ssh_key_path: str
    container_image: str
    callback_url: HttpUrl
    volume_name: str = "app_data"
    db_type: str = None
    db_user: str = None
    db_password: str = None
    db_name: str = None

    @validator("server_ip")
    def validate_ip(cls, v):
        ipaddress.ip_address(v)
        return v

    @validator("ssh_key_path")
    def validate_ssh_key(cls, v):
        if not os.path.isfile(v) or not os.access(v, os.R_OK):
            raise ValueError("SSH key path must be a readable file")
        return v

    @validator("db_type")
    def validate_db_type(cls, v):
        if v and v not in ["postgres", "mysql"]:
            raise ValueError("db_type must be 'postgres', 'mysql', or null")
        return v

    @validator("db_user", "db_password", "db_name")
    def validate_db_fields(cls, v, values, field):
        if values.get("db_type") and not v:
            raise ValueError(f"{field.name} is required when db_type is specified")
        return v

class BackupRequest(BaseModel):
    server_ip: str
    ssh_user: str
    ssh_key_path: str
    container_name: str
    backup_image_name: str
    callback_url: HttpUrl
    volume_name: str = "app_data"
    db_type: str = None
    db_user: str = None
    db_password: str = None
    db_name: str = None

    @validator("server_ip")
    def validate_ip(cls, v):
        ipaddress.ip_address(v)
        return v

    @validator("ssh_key_path")
    def validate_ssh_key(cls, v):
        if not os.path.isfile(v) or not os.access(v, os.R_OK):
            raise ValueError("SSH key path must be a readable file")
        return v

    @validator("db_type")
    def validate_db_type(cls, v):
        if v and v not in ["postgres", "mysql"]:
            raise ValueError("db_type must be 'postgres', 'mysql', or null")
        return v

class RestoreRequest(BaseModel):
    server_ip: str
    ssh_user: str
    ssh_key_path: str
    container_name: str
    backup_image_file: str
    callback_url: HttpUrl
    volume_name: str = "app_data"
    db_type: str = None
    db_user: str = None
    db_password: str = None
    db_name: str = None
    backup_db_file: str = None

    @validator("server_ip")
    def validate_ip(cls, v):
        ipaddress.ip_address(v)
        return v

    @validator("ssh_key_path")
    def validate_ssh_key(cls, v):
        if not os.path.isfile(v) or not os.access(v, os.R_OK):
            raise ValueError("SSH key path must be a readable file")
        return v

    @validator("backup_image_file", "backup_db_file")
    def validate_file(cls, v, values, field):
        if v and not os.path.isfile(v):
            raise ValueError(f"{field.name} must be a valid file path")
        if values.get("db_type") and field.name == "backup_db_file" and not v:
            raise ValueError("backup_db_file is required when db_type is specified")
        return v

    @validator("db_type")
    def validate_db_type(cls, v):
        if v and v not in ["postgres", "mysql"]:
            raise ValueError("db_type must be 'postgres', 'mysql', or null")
        return v

class RemoveRequest(BaseModel):
    server_ip: str
    ssh_user: str
    ssh_key_path: str
    container_name: str
    callback_url: HttpUrl
    volume_name: str = "app_data"

    @validator("server_ip")
    def validate_ip(cls, v):
        ipaddress.ip_address(v)
        return v

    @validator("ssh_key_path")
    def validate_ssh_key(cls, v):
        if not os.path.isfile(v) or not os.access(v, os.R_OK):
            raise ValueError("SSH key path must be a readable file")
        return v