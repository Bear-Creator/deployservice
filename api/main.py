from fastapi import FastAPI, BackgroundTasks
from models.deploy import DeployRequest, BackupRequest, RestoreRequest, RemoveRequest
from services.deployment import run_deployment, run_backup, run_restore, run_remove

app = FastAPI()

@app.post("/deploy")
async def deploy_application(request: DeployRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_deployment, request)
    return {"message": "Deployment started", "server_ip": request.server_ip}

@app.post("/backup")
async def backup_application(request: BackupRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_backup, request)
    return {"message": "Backup started", "server_ip": request.server_ip}

@app.post("/restore")
async def restore_application(request: RestoreRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_restore, request)
    return {"message": "Restore started", "server_ip": request.server_ip}

@app.post("/remove")
async def remove_application(request: RemoveRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_remove, request)
    return {"message": "Remove started", "server_ip": request.server_ip}