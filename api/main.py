from fastapi import FastAPI
from api.routes import incidents, copilot, health, dashboard

app = FastAPI(title="Autonomous AI Ops Platform", version="2.0.0")

app.include_router(health.router,     prefix="/health",     tags=["Health"])
app.include_router(incidents.router,  prefix="/incidents",  tags=["Incidents"])
app.include_router(copilot.router,    prefix="/copilot",    tags=["Copilot"])
app.include_router(dashboard.router,  prefix="/dashboard",  tags=["Dashboard"])

@app.on_event("startup")
async def startup():
    print("AI Ops Platform started")
    print("Dashboard: http://localhost:8000/dashboard/")
    print("API Docs:  http://localhost:8000/docs")
