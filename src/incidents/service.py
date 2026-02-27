from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.models import Incident
from src.incidents.schemas import IncidentCreate, SuiviCreate
from src.models import SuiviIncident

async def create_incident(db: AsyncSession, incident_data: IncidentCreate):
    new_incident = Incident(**incident_data.model_dump())
    db.add(new_incident)
    await db.commit()
    await db.refresh(new_incident)
    return new_incident

async def get_incident(db: AsyncSession, incident_id: int):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    return result.scalar_one_or_none()

async def get_patient_incidents(db: AsyncSession, patient_id: int):
    result = await db.execute(select(Incident).where(Incident.id_patient == patient_id))
    return result.scalars().all()

async def update_incident(db: AsyncSession, incident_id: int, data: dict):
    await db.execute(update(Incident).where(Incident.id == incident_id).values(**data))
    await db.commit()
    return await get_incident(db, incident_id)


async def add_suivi(db: AsyncSession, incident_id: int, suivi_data: SuiviCreate):
    new_suivi = SuiviIncident(**suivi_data.model_dump(), id_incident=incident_id)
    db.add(new_suivi)
    await db.commit()
    await db.refresh(new_suivi)
    return new_suivi

async def get_suivis_by_incident(db: AsyncSession, incident_id: int):
    result = await db.execute(select(SuiviIncident).where(SuiviIncident.id_incident == incident_id))
    return result.scalars().all()