# Manuel Utilisateur — FollowUp
## Section : Déclaration d'un Incident

---

### Description

La fonctionnalité de déclaration d'incident permet à un patient ou à un membre de l'équipe médicale de signaler un problème lié à un implant cochléaire. Chaque incident est enregistré, suivi et tracé conformément aux exigences réglementaires (IEC 62304).

---

### Prérequis

- Disposer d'un compte FollowUp actif
- Connaître l'identifiant du patient concerné (`id_patient`)
- Avoir accès à l'API FollowUp (URL de base : `http://localhost:8000`)

---

### Étapes détaillées

#### 1. Créer un incident

Envoyez une requête `POST` à `/api/incidents/` avec le corps JSON suivant :

```json
{
  "date_incident": "2024-06-15T10:30:00",
  "heure_incident": "2024-06-15T10:30:00",
  "gravite": "Mineur",
  "description": "Perte auditive légère détectée après réglage du processeur.",
  "id_patient": 1,
  "id_medecin": 3
}
```

**Champs obligatoires :**
- `date_incident` — date de l'incident (format ISO 8601)
- `heure_incident` — heure de l'incident (format ISO 8601)
- `gravite` — niveau de gravité : `Mineur`, `Modéré`, `Majeur`, ou `Critique`
- `description` — description de l'incident (maximum 2000 caractères)
- `id_patient` — identifiant du patient

**Champs optionnels :**
- `id_medecin` — identifiant du médecin référent

En cas de succès, la réponse retourne le code **201** et l'incident créé avec son `id` et son statut `Ouvert`.

#### 2. Consulter un incident

```
GET /api/incidents/{id}
```

Retourne les détails de l'incident. Si l'incident a été supprimé ou n'existe pas, la réponse sera **404**.

#### 3. Lister les incidents d'un patient

```
GET /api/incidents/patient/{id_patient}
```

Retourne la liste de tous les incidents actifs du patient.

#### 4. Mettre à jour un incident

```
PUT /api/incidents/{id}
```

Corps : dictionnaire des champs à modifier. Exemple :
```json
{ "statut": "EnCours", "description": "Symptômes persistants." }
```

#### 5. Supprimer un incident

```
DELETE /api/incidents/{id}
```

L'incident est **marqué comme supprimé** (soft delete) mais reste conservé en base pour des raisons de traçabilité réglementaire. La réponse est **204 No Content**.

#### 6. Ajouter un suivi

```
POST /api/incidents/{id}/suivis
```

```json
{
  "actions_prises": "Réglage effectué. Patient convoqué dans 15 jours.",
  "id_medecin": 2
}
```

#### 7. Consulter l'historique des suivis

```
GET /api/incidents/{id}/suivis
```

Retourne la liste chronologique de toutes les actions prises sur l'incident.

---

### Messages d'erreur courants

| Code | Message | Cause | Solution |
|------|---------|-------|----------|
| 404 | "Incident non trouvé" | ID inexistant ou incident supprimé | Vérifier l'ID |
| 422 | Erreur de validation | Champ manquant ou invalide | Vérifier le format des données |
| 422 | Gravité non valide | Valeur hors enum | Utiliser : Mineur, Modéré, Majeur, Critique |
| 422 | Description trop longue | > 2000 caractères | Raccourcir la description |
| 500 | Erreur interne | Problème serveur | Contacter l'administrateur |