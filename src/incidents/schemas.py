from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from src.models import StatutIncident

class IncidentCreate(BaseModel):
    date_incident: datetime
    heure_incident: datetime
    gravite: str = Field(..., pattern="^(Mineur|Modéré|Majeur|Critique)$")
    description: str = Field(..., max_length=2000)
    id_patient: int
    id_medecin: Optional[int] = None

class IncidentRead(IncidentCreate):
    id: int
    statut: StatutIncident
    # date_creation supprimé car il n'existe pas dans votre modèle SQLAlchemy
    
    class Config:
        from_attributes = True

class SuiviCreate(BaseModel):
    actions_prises: str = Field(..., max_length=2000)
    id_medecin: int

class SuiviRead(SuiviCreate):
    id: int
    date_suivi: datetime
    id_incident: int
    
    class Config:
        from_attributes = True