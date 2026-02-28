"""
Tests unitaires — Partie 2.1 & 2.2 (IEC 62304 Classe B)

Couvre :
- Validation des données (schémas Pydantic)
- Logique métier (service layer)
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.incidents.schemas import IncidentCreate, SuiviCreate


# ==============================================================================
# 2.1 — Tests unitaires : Validation des données (Schémas Pydantic)
# ==============================================================================

class TestIncidentCreateValidation:
    """Tests de validation du schéma IncidentCreate."""

    def _valid_payload(self) -> dict:
        """Retourne un payload valide de base."""
        return {
            "date_incident": datetime(2024, 6, 15, 10, 30),
            "heure_incident": datetime(2024, 6, 15, 10, 30),
            "gravite": "Mineur",
            "description": "Perte auditive légère détectée après réglage.",
            "id_patient": 1,
        }

    # --- Cas nominaux ---

    def test_valid_incident_mineur(self):
        """Cas nominal : création d'un incident de gravité Mineur."""
        payload = self._valid_payload()
        incident = IncidentCreate(**payload)
        assert incident.gravite == "Mineur"
        assert incident.id_patient == 1

    def test_valid_incident_modere(self):
        """Cas nominal : gravité Modéré acceptée."""
        payload = self._valid_payload()
        payload["gravite"] = "Modéré"
        incident = IncidentCreate(**payload)
        assert incident.gravite == "Modéré"

    def test_valid_incident_majeur(self):
        """Cas nominal : gravité Majeur acceptée."""
        payload = self._valid_payload()
        payload["gravite"] = "Majeur"
        incident = IncidentCreate(**payload)
        assert incident.gravite == "Majeur"

    def test_valid_incident_critique(self):
        """Cas nominal : gravité Critique acceptée."""
        payload = self._valid_payload()
        payload["gravite"] = "Critique"
        incident = IncidentCreate(**payload)
        assert incident.gravite == "Critique"

    def test_valid_incident_with_optional_medecin(self):
        """Cas nominal : champ id_medecin optionnel accepté."""
        payload = self._valid_payload()
        payload["id_medecin"] = 42
        incident = IncidentCreate(**payload)
        assert incident.id_medecin == 42

    def test_valid_incident_medecin_none(self):
        """Cas nominal : id_medecin absent → None par défaut."""
        payload = self._valid_payload()
        incident = IncidentCreate(**payload)
        assert incident.id_medecin is None

    # --- Cas d'erreur : champs manquants ---

    def test_missing_description_raises_error(self):
        """Erreur : description manquante."""
        payload = self._valid_payload()
        del payload["description"]
        with pytest.raises(ValidationError) as exc_info:
            IncidentCreate(**payload)
        assert "description" in str(exc_info.value)

    def test_missing_id_patient_raises_error(self):
        """Erreur : id_patient manquant."""
        payload = self._valid_payload()
        del payload["id_patient"]
        with pytest.raises(ValidationError) as exc_info:
            IncidentCreate(**payload)
        assert "id_patient" in str(exc_info.value)

    def test_missing_gravite_raises_error(self):
        """Erreur : gravite manquante."""
        payload = self._valid_payload()
        del payload["gravite"]
        with pytest.raises(ValidationError):
            IncidentCreate(**payload)

    def test_missing_date_incident_raises_error(self):
        """Erreur : date_incident manquante."""
        payload = self._valid_payload()
        del payload["date_incident"]
        with pytest.raises(ValidationError):
            IncidentCreate(**payload)

    # --- Cas d'erreur : valeurs invalides ---

    def test_invalid_gravite_raises_error(self):
        """Erreur : gravité non reconnue → validation échoue."""
        payload = self._valid_payload()
        payload["gravite"] = "Catastrophique"  # Non autorisé
        with pytest.raises(ValidationError) as exc_info:
            IncidentCreate(**payload)
        assert "gravite" in str(exc_info.value)

    def test_gravite_lowercase_raises_error(self):
        """Erreur : gravité en minuscules → le pattern est sensible à la casse."""
        payload = self._valid_payload()
        payload["gravite"] = "mineur"
        with pytest.raises(ValidationError):
            IncidentCreate(**payload)

    def test_description_too_long_raises_error(self):
        """Erreur : description dépasse 2000 caractères."""
        payload = self._valid_payload()
        payload["description"] = "A" * 2001
        with pytest.raises(ValidationError) as exc_info:
            IncidentCreate(**payload)
        assert "description" in str(exc_info.value)

    def test_description_exactly_2000_chars_is_valid(self):
        """Limite : description de exactement 2000 caractères → valide."""
        payload = self._valid_payload()
        payload["description"] = "B" * 2000
        incident = IncidentCreate(**payload)
        assert len(incident.description) == 2000

    def test_invalid_date_format_raises_error(self):
        """Erreur : format de date invalide."""
        payload = self._valid_payload()
        payload["date_incident"] = "pas-une-date"
        with pytest.raises(ValidationError):
            IncidentCreate(**payload)


class TestSuiviCreateValidation:
    """Tests de validation du schéma SuiviCreate."""

    def test_valid_suivi(self):
        """Cas nominal : suivi valide."""
        suivi = SuiviCreate(actions_prises="Réglage du processeur effectué.", id_medecin=5)
        assert suivi.id_medecin == 5

    def test_missing_actions_prises_raises_error(self):
        """Erreur : actions_prises manquant."""
        with pytest.raises(ValidationError):
            SuiviCreate(id_medecin=5)

    def test_missing_id_medecin_raises_error(self):
        """Erreur : id_medecin manquant."""
        with pytest.raises(ValidationError):
            SuiviCreate(actions_prises="Test action")

    def test_actions_prises_too_long_raises_error(self):
        """Erreur : actions_prises dépasse 2000 caractères."""
        with pytest.raises(ValidationError):
            SuiviCreate(actions_prises="X" * 2001, id_medecin=1)


# ==============================================================================
# 2.2 — Tests unitaires : Logique métier (Service Layer)
# ==============================================================================

class TestIncidentServiceLogic:
    """Tests de la logique métier du service incidents."""

    @pytest.mark.asyncio
    async def test_create_incident_sets_default_status(self, test_db):
        """
        Logique métier : un incident créé a automatiquement le statut OUVERT
        et is_deleted = False.
        """
        from src.incidents.service import create_incident
        from src.models import StatutIncident

        data = IncidentCreate(
            date_incident=datetime(2024, 6, 15, 10, 0),
            heure_incident=datetime(2024, 6, 15, 10, 0),
            gravite="Mineur",
            description="Test création automatique statut.",
            id_patient=1,
        )

        incident = await create_incident(test_db, data)

        assert incident.id is not None, "L'ID doit être auto-généré"
        assert incident.statut == StatutIncident.OUVERT, "Le statut initial doit être OUVERT"
        assert incident.is_deleted is False, "is_deleted doit être False à la création"

    @pytest.mark.asyncio
    async def test_get_incident_returns_none_for_unknown_id(self, test_db):
        """Logique métier : récupérer un ID inexistant retourne None."""
        from src.incidents.service import get_incident

        result = await get_incident(test_db, 9999)
        assert result is None

    @pytest.mark.asyncio
    async def test_soft_delete_hides_incident(self, test_db):
        """
        Logique métier : après soft delete, l'incident n'est plus accessible via get_incident.
        Le record reste en base (traçabilité IEC 62304).
        """
        from src.incidents.service import create_incident, delete_incident, get_incident
        from sqlalchemy import select
        from src.models import Incident

        data = IncidentCreate(
            date_incident=datetime(2024, 6, 15, 10, 0),
            heure_incident=datetime(2024, 6, 15, 10, 0),
            gravite="Majeur",
            description="Test soft delete.",
            id_patient=1,
        )

        incident = await create_incident(test_db, data)
        incident_id = incident.id

        deleted = await delete_incident(test_db, incident_id)
        assert deleted is True

        # get_incident ne doit plus le retourner
        result = await get_incident(test_db, incident_id)
        assert result is None, "L'incident supprimé ne doit pas être accessible"

        # Mais il existe toujours en base (audit)
        raw = await test_db.execute(select(Incident).where(Incident.id == incident_id))
        raw_incident = raw.scalar_one_or_none()
        assert raw_incident is not None, "L'incident doit toujours exister en BDD"
        assert raw_incident.is_deleted is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent_incident_returns_false(self, test_db):
        """Logique métier : supprimer un ID inexistant retourne False."""
        from src.incidents.service import delete_incident

        result = await delete_incident(test_db, 99999)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_patient_incidents_excludes_deleted(self, test_db):
        """
        Logique métier : la liste des incidents d'un patient exclut les incidents soft-deleted.
        """
        from src.incidents.service import create_incident, delete_incident, get_patient_incidents

        payload = dict(
            date_incident=datetime(2024, 6, 15, 10, 0),
            heure_incident=datetime(2024, 6, 15, 10, 0),
            gravite="Mineur",
            description="Incident actif.",
            id_patient=10,
        )

        i1 = await create_incident(test_db, IncidentCreate(**payload))
        payload["description"] = "Incident à supprimer."
        i2 = await create_incident(test_db, IncidentCreate(**payload))

        await delete_incident(test_db, i2.id)

        incidents = await get_patient_incidents(test_db, 10)
        ids = [i.id for i in incidents]

        assert i1.id in ids
        assert i2.id not in ids, "L'incident supprimé ne doit pas apparaître dans la liste"

    @pytest.mark.asyncio
    async def test_update_incident_modifies_field(self, test_db):
        """Logique métier : la mise à jour modifie bien le champ demandé."""
        from src.incidents.service import create_incident, update_incident

        data = IncidentCreate(
            date_incident=datetime(2024, 6, 15, 10, 0),
            heure_incident=datetime(2024, 6, 15, 10, 0),
            gravite="Mineur",
            description="Description initiale.",
            id_patient=2,
        )

        incident = await create_incident(test_db, data)
        updated = await update_incident(test_db, incident.id, {"description": "Description modifiée."})

        assert updated.description == "Description modifiée."

    @pytest.mark.asyncio
    async def test_add_suivi_links_to_incident(self, test_db):
        """Logique métier : un suivi est bien rattaché à l'incident."""
        from src.incidents.service import create_incident, add_suivi, get_suivis_by_incident

        incident_data = IncidentCreate(
            date_incident=datetime(2024, 6, 15, 10, 0),
            heure_incident=datetime(2024, 6, 15, 10, 0),
            gravite="Critique",
            description="Panne totale du processeur.",
            id_patient=3,
        )

        incident = await create_incident(test_db, incident_data)

        suivi_data = SuiviCreate(
            actions_prises="Remplacement du processeur en urgence.",
            id_medecin=1,
        )

        suivi = await add_suivi(test_db, incident.id, suivi_data)
        assert suivi.id_incident == incident.id
        assert suivi.id is not None

        suivis = await get_suivis_by_incident(test_db, incident.id)
        assert len(suivis) == 1
        assert suivis[0].actions_prises == "Remplacement du processeur en urgence."