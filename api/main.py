from fastapi import FastAPI, BackgroundTasks
from models.deploy import DeployRequest
from services.deployment import run_deployment

app = FastAPI()

@app.post("/deploy")
async def deploy_application(request: DeployRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_deployment, request)
    return {"message": "Deployment started", "server_ip": request.server_ip}