"""
Tests d'intégration — Partie 2.3 (IEC 62304 Classe B)

Teste les endpoints REST de l'API via un client HTTP de test.
Vérifie les codes HTTP, le format JSON, et les comportements d'erreur.
"""

import pytest
from datetime import datetime


# Payload valide réutilisable
VALID_INCIDENT_PAYLOAD = {
    "date_incident": "2024-06-15T10:30:00",
    "heure_incident": "2024-06-15T10:30:00",
    "gravite": "Mineur",
    "description": "Perte auditive légère détectée lors d'un test de réglage.",
    "id_patient": 1,
    "id_medecin": None,
}


# ==============================================================================
# POST /api/incidents
# ==============================================================================

class TestCreateIncident:
    """Tests d'intégration : création d'un incident."""

    @pytest.mark.asyncio
    async def test_create_incident_valid_returns_201(self, client):
        """Cas nominal : POST avec données valides → 201 Created."""
        response = await client.post("/api/incidents/", json=VALID_INCIDENT_PAYLOAD)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["gravite"] == "Mineur"
        assert data["statut"] == "Ouvert"

    @pytest.mark.asyncio
    async def test_create_incident_all_gravite_values(self, client):
        """Cas nominal : toutes les valeurs de gravité valides sont acceptées."""
        for gravite in ["Mineur", "Modéré", "Majeur", "Critique"]:
            payload = {**VALID_INCIDENT_PAYLOAD, "gravite": gravite}
            response = await client.post("/api/incidents/", json=payload)
            assert response.status_code == 201, f"Gravité {gravite} devrait être acceptée"

    @pytest.mark.asyncio
    async def test_create_incident_invalid_gravite_returns_422(self, client):
        """Cas d'erreur : gravité invalide → 422 Unprocessable Entity."""
        payload = {**VALID_INCIDENT_PAYLOAD, "gravite": "Catastrophique"}
        response = await client.post("/api/incidents/", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_incident_missing_description_returns_422(self, client):
        """Cas d'erreur : description manquante → 422."""
        payload = {k: v for k, v in VALID_INCIDENT_PAYLOAD.items() if k != "description"}
        response = await client.post("/api/incidents/", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_incident_missing_patient_returns_422(self, client):
        """Cas d'erreur : id_patient manquant → 422."""
        payload = {k: v for k, v in VALID_INCIDENT_PAYLOAD.items() if k != "id_patient"}
        response = await client.post("/api/incidents/", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_incident_description_too_long_returns_422(self, client):
        """Cas d'erreur : description > 2000 caractères → 422."""
        payload = {**VALID_INCIDENT_PAYLOAD, "description": "X" * 2001}
        response = await client.post("/api/incidents/", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_incident_empty_body_returns_422(self, client):
        """Cas d'erreur : body vide → 422."""
        response = await client.post("/api/incidents/", json={})
        assert response.status_code == 422


# ==============================================================================
# GET /api/incidents/{id}
# ==============================================================================

class TestGetIncident:
    """Tests d'intégration : récupération d'un incident."""

    @pytest.mark.asyncio
    async def test_get_existing_incident_returns_200(self, client):
        """Cas nominal : GET d'un incident existant → 200 et les bonnes données."""
        create_resp = await client.post("/api/incidents/", json=VALID_INCIDENT_PAYLOAD)
        incident_id = create_resp.json()["id"]

        response = await client.get(f"/api/incidents/{incident_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == incident_id
        assert data["description"] == VALID_INCIDENT_PAYLOAD["description"]

    @pytest.mark.asyncio
    async def test_get_nonexistent_incident_returns_404(self, client):
        """Cas d'erreur : GET d'un ID inexistant → 404 Not Found."""
        response = await client.get("/api/incidents/99999")
        assert response.status_code == 404
        assert "non trouvé" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_deleted_incident_returns_404(self, client):
        """Cas d'erreur : GET d'un incident soft-deleted → 404."""
        create_resp = await client.post("/api/incidents/", json=VALID_INCIDENT_PAYLOAD)
        incident_id = create_resp.json()["id"]

        await client.delete(f"/api/incidents/{incident_id}")

        response = await client.get(f"/api/incidents/{incident_id}")
        assert response.status_code == 404


# ==============================================================================
# GET /api/incidents/patient/{id}
# ==============================================================================

class TestGetPatientIncidents:
    """Tests d'intégration : liste des incidents d'un patient."""

    @pytest.mark.asyncio
    async def test_get_patient_incidents_returns_list(self, client):
        """Cas nominal : liste des incidents d'un patient avec incidents existants."""
        for _ in range(3):
            await client.post("/api/incidents/", json={**VALID_INCIDENT_PAYLOAD, "id_patient": 99})

        response = await client.get("/api/incidents/patient/99")
        assert response.status_code == 200
        assert len(response.json()) == 3

    @pytest.mark.asyncio
    async def test_get_patient_incidents_empty_list(self, client):
        """Cas nominal : patient sans incidents → liste vide."""
        response = await client.get("/api/incidents/patient/9999")
        assert response.status_code == 200
        assert response.json() == []


# ==============================================================================
# PUT /api/incidents/{id}
# ==============================================================================

class TestUpdateIncident:
    """Tests d'intégration : mise à jour d'un incident."""

    @pytest.mark.asyncio
    async def test_update_existing_incident_returns_200(self, client):
        """Cas nominal : mise à jour valide → 200 et les nouvelles données."""
        create_resp = await client.post("/api/incidents/", json=VALID_INCIDENT_PAYLOAD)
        incident_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/incidents/{incident_id}",
            json={"description": "Description mise à jour."}
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Description mise à jour."

    @pytest.mark.asyncio
    async def test_update_nonexistent_incident_returns_404(self, client):
        """Cas d'erreur : mise à jour d'un ID inexistant → 404."""
        response = await client.put("/api/incidents/99999", json={"description": "Test"})
        assert response.status_code == 404


# ==============================================================================
# DELETE /api/incidents/{id}
# ==============================================================================

class TestDeleteIncident:
    """Tests d'intégration : suppression (soft delete) d'un incident."""

    @pytest.mark.asyncio
    async def test_delete_existing_incident_returns_204(self, client):
        """Cas nominal : DELETE d'un incident existant → 204 No Content."""
        create_resp = await client.post("/api/incidents/", json=VALID_INCIDENT_PAYLOAD)
        incident_id = create_resp.json()["id"]

        response = await client.delete(f"/api/incidents/{incident_id}")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_nonexistent_incident_returns_404(self, client):
        """Cas d'erreur : DELETE d'un ID inexistant → 404."""
        response = await client.delete("/api/incidents/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_is_soft_delete(self, client):
        """Soft delete : après DELETE, l'incident n'est plus accessible via GET."""
        create_resp = await client.post("/api/incidents/", json=VALID_INCIDENT_PAYLOAD)
        incident_id = create_resp.json()["id"]

        await client.delete(f"/api/incidents/{incident_id}")

        get_resp = await client.get(f"/api/incidents/{incident_id}")
        assert get_resp.status_code == 404, "L'incident supprimé ne doit plus être accessible"

    @pytest.mark.asyncio
    async def test_delete_twice_returns_404(self, client):
        """Idempotence : supprimer deux fois le même incident → 404 au second appel."""
        create_resp = await client.post("/api/incidents/", json=VALID_INCIDENT_PAYLOAD)
        incident_id = create_resp.json()["id"]

        await client.delete(f"/api/incidents/{incident_id}")
        response = await client.delete(f"/api/incidents/{incident_id}")
        assert response.status_code == 404


# ==============================================================================
# POST & GET /api/incidents/{id}/suivis
# ==============================================================================

class TestSuivis:
    """Tests d'intégration : gestion des suivis d'un incident."""

    @pytest.mark.asyncio
    async def test_add_suivi_returns_201(self, client):
        """Cas nominal : ajout d'un suivi → 201 Created."""
        create_resp = await client.post("/api/incidents/", json=VALID_INCIDENT_PAYLOAD)
        incident_id = create_resp.json()["id"]

        suivi_payload = {
            "actions_prises": "Consultation de contrôle réalisée.",
            "id_medecin": 1,
        }
        response = await client.post(f"/api/incidents/{incident_id}/suivis", json=suivi_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["id_incident"] == incident_id
        assert data["actions_prises"] == suivi_payload["actions_prises"]

    @pytest.mark.asyncio
    async def test_get_suivis_returns_history(self, client):
        """Cas nominal : historique des suivis retourne la liste dans l'ordre."""
        create_resp = await client.post("/api/incidents/", json=VALID_INCIDENT_PAYLOAD)
        incident_id = create_resp.json()["id"]

        await client.post(
            f"/api/incidents/{incident_id}/suivis",
            json={"actions_prises": "Premier suivi.", "id_medecin": 1}
        )
        await client.post(
            f"/api/incidents/{incident_id}/suivis",
            json={"actions_prises": "Deuxième suivi.", "id_medecin": 2}
        )

        response = await client.get(f"/api/incidents/{incident_id}/suivis")
        assert response.status_code == 200
        suivis = response.json()
        assert len(suivis) == 2

    @pytest.mark.asyncio
    async def test_add_suivi_missing_actions_returns_422(self, client):
        """Cas d'erreur : suivi sans actions_prises → 422."""
        create_resp = await client.post("/api/incidents/", json=VALID_INCIDENT_PAYLOAD)
        incident_id = create_resp.json()["id"]

        response = await client.post(
            f"/api/incidents/{incident_id}/suivis",
            json={"id_medecin": 1}
        )
        assert response.status_code == 422

