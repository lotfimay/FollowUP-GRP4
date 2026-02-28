"""
Router for the incidents module.
Exposes REST endpoints for CRUD operations on incidents and suivis.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.incidents import service, schemas

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.IncidentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouvel incident",
    description="Déclare un nouvel incident lié à un patient. Le statut est automatiquement défini à 'Ouvert'."
)
async def create_incident(data: schemas.IncidentCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_incident(db, data)


@router.get(
    "/patient/{patient_id}",
    response_model=list[schemas.IncidentRead],
    summary="Liste des incidents d'un patient",
    description="Retourne tous les incidents actifs (non supprimés) d'un patient donné."
)
async def read_patient_incidents(patient_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_patient_incidents(db, patient_id)


@router.get(
    "/{incident_id}",
    response_model=schemas.IncidentRead,
    summary="Récupérer un incident par ID",
    description="Retourne les détails d'un incident. Retourne 404 si l'incident n'existe pas ou a été supprimé."
)
async def read_incident(incident_id: int, db: AsyncSession = Depends(get_db)):
    incident = await service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident non trouvé")
    return incident



@router.put(
    "/{incident_id}",
    response_model=schemas.IncidentRead,
    summary="Mettre à jour un incident",
    description="Met à jour les champs d'un incident existant. Retourne 404 si l'incident est introuvable."
)
async def update_incident(incident_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    updated = await service.update_incident(db, incident_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Incident non trouvé")
    return updated


@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un incident (soft delete)",
    description=(
        "Marque l'incident comme supprimé (is_deleted=True) sans l'effacer physiquement de la base. "
        "Cela garantit la traçabilité conformément à la norme IEC 62304."
    )
)
async def delete_incident(incident_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await service.delete_incident(db, incident_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Incident non trouvé")
    # 204 No Content — pas de body retourné


@router.post(
    "/{incident_id}/suivis",
    response_model=schemas.SuiviRead,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un suivi à un incident",
    description="Enregistre une action médicale prise sur un incident existant."
)
async def add_suivi_to_incident(incident_id: int, data: schemas.SuiviCreate, db: AsyncSession = Depends(get_db)):
    return await service.add_suivi(db, incident_id, data)


@router.get(
    "/{incident_id}/suivis",
    response_model=list[schemas.SuiviRead],
    summary="Historique des suivis d'un incident",
    description="Retourne la liste chronologique de tous les suivis enregistrés pour un incident."
)
async def get_suivis_incident(incident_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_suivis_by_incident(db, incident_id)