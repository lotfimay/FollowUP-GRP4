from fastapi import FastAPI
from src.incidents.router import router as incident_router

app = FastAPI(title="FollowUp API")

app.include_router(incident_router, prefix="/api/incidents", tags=["Incidents"])