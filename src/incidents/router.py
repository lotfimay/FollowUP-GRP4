from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.incidents import service, schemas

router = APIRouter()

@router.post("/", response_model=schemas.IncidentRead, status_code=status.HTTP_201_CREATED)
async def create_incident(data: schemas.IncidentCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_incident(db, data)

@router.get("/{incident_id}", response_model=schemas.IncidentRead)
async def read_incident(incident_id: int, db: AsyncSession = Depends(get_db)):
    incident = await service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident non trouvé")
    return incident

@router.get("/patient/{patient_id}")
async def read_patient_incidents(patient_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_patient_incidents(db, patient_id)

@router.put("/{incident_id}")
async def update_incident(incident_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    updated = await service.update_incident(db, incident_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Incident non trouvé")
    return updated

@router.post("/{incident_id}/suivis", response_model=schemas.SuiviRead)
async def add_suivi_to_incident(incident_id: int, data: schemas.SuiviCreate, db: AsyncSession = Depends(get_db)):
    return await service.add_suivi(db, incident_id, data)

@router.get("/{incident_id}/suivis", response_model=list[schemas.SuiviRead])
async def get_suivis_incident(incident_id: int, db: AsyncSession = Depends(get_db)):
    # Modifiez ici pour appeler la bonne fonction définie dans service.py
    return await service.get_suivis_by_incident(db, incident_id)