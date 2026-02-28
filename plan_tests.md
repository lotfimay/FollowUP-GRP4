# Plan de Tests — Module Incidents FollowUp
## Conformité IEC 62304 — Classe B

---

## 1. Objectifs

Valider que le module de gestion des incidents de l'application FollowUp répond aux exigences fonctionnelles et non-fonctionnelles définies, avec un niveau de rigueur conforme à la classification **Classe B** de la norme IEC 62304 (blessure possible sans risque vital).

---

## 2. Périmètre

| Inclus | Exclus |
|--------|--------|
| Validation des données (schémas Pydantic) | Authentification / autorisation |
| Logique métier du service | Tests de performance / charge |
| Endpoints REST de l'API | Interface utilisateur frontend |
| Soft delete et traçabilité | Autres modules (patients, implants) |
| Gestion des suivis (suivi incidents) | |

---

## 3. Environnement de test

- **Langage** : Python 3.11+
- **Framework de test** : pytest + pytest-asyncio
- **Base de données** : SQLite en mémoire (aiosqlite) — isolation totale entre tests
- **Client HTTP** : httpx (AsyncClient avec ASGITransport)
- **Couverture** : pytest-cov — objectif ≥ 80% sur `src/incidents/`

---

## 4. Données de test

- Patients fictifs avec `id_patient` entiers (1, 2, 3...)
- Médecins fictifs avec `id_medecin` entiers
- Dates : valeurs fixes ISO 8601 (ex: `2024-06-15T10:30:00`)
- Gravités testées : Mineur, Modéré, Majeur, Critique
- Descriptions valides (≤ 2000 chars) et invalides (> 2000 chars)

---

## 5. Cas de tests

### 5.1 Tests unitaires — Validation des données

| ID | Description | Résultat attendu |
|----|-------------|-----------------|
| TV-01 | Incident valide avec gravité Mineur | Objet créé sans erreur |
| TV-02 | Incident valide avec gravité Critique | Objet créé sans erreur |
| TV-03 | Description de 2000 caractères exactement | Valide |
| TV-04 | Description de 2001 caractères | ValidationError |
| TV-05 | Gravité non reconnue ("Catastrophique") | ValidationError |
| TV-06 | Gravité en minuscules ("mineur") | ValidationError |
| TV-07 | description manquante | ValidationError |
| TV-08 | id_patient manquant | ValidationError |
| TV-09 | date_incident format invalide ("pas-une-date") | ValidationError |
| TV-10 | id_medecin absent → None par défaut | Valide |

### 5.2 Tests unitaires — Logique métier

| ID | Description | Résultat attendu |
|----|-------------|-----------------|
| TM-01 | Création → statut OUVERT automatique | statut == "Ouvert" |
| TM-02 | Création → is_deleted False automatique | is_deleted == False |
| TM-03 | Création → id auto-généré non null | id != None |
| TM-04 | get_incident avec ID inexistant | Retourne None |
| TM-05 | Soft delete → get_incident retourne None | None après delete |
| TM-06 | Soft delete → record toujours en BDD | is_deleted == True en BDD |
| TM-07 | delete_incident ID inexistant | Retourne False |
| TM-08 | get_patient_incidents exclut soft-deleted | Incident supprimé absent |
| TM-09 | update_incident modifie le champ | Champ mis à jour |
| TM-10 | add_suivi lie l'incident et le médecin | id_incident correct |

### 5.3 Tests d'intégration API REST

| ID | Endpoint | Scénario | Code HTTP attendu |
|----|----------|----------|-------------------|
| TI-01 | POST /api/incidents/ | Données valides | 201 |
| TI-02 | POST /api/incidents/ | Gravité invalide | 422 |
| TI-03 | POST /api/incidents/ | Description trop longue | 422 |
| TI-04 | POST /api/incidents/ | Body vide | 422 |
| TI-05 | GET /api/incidents/{id} | ID existant | 200 |
| TI-06 | GET /api/incidents/{id} | ID inexistant | 404 |
| TI-07 | GET /api/incidents/{id} | ID soft-deleted | 404 |
| TI-08 | GET /api/incidents/patient/{id} | Patient avec incidents | 200 + liste |
| TI-09 | GET /api/incidents/patient/{id} | Patient sans incidents | 200 + [] |
| TI-10 | PUT /api/incidents/{id} | Mise à jour valide | 200 |
| TI-11 | PUT /api/incidents/{id} | ID inexistant | 404 |
| TI-12 | DELETE /api/incidents/{id} | ID existant | 204 |
| TI-13 | DELETE /api/incidents/{id} | ID inexistant | 404 |
| TI-14 | DELETE /api/incidents/{id} | Soft delete vérifié via GET | 404 après DELETE |
| TI-15 | DELETE deux fois même ID | 2ème appel | 404 |
| TI-16 | POST /api/incidents/{id}/suivis | Données valides | 201 |
| TI-17 | POST /api/incidents/{id}/suivis | actions_prises manquant | 422 |
| TI-18 | GET /api/incidents/{id}/suivis | Historique correct | 200 + liste |

---

## 6. Critères de réussite

- Tous les tests doivent passer (0 échec)
- Couverture de code ≥ 80% sur `src/incidents/`
- Codes HTTP conformes aux spécifications REST
- Soft delete : données non supprimées physiquement de la BDD

---

## 7. Responsabilités

| Rôle | Responsable        |
|------|--------------------|
| Rédaction du plan de tests | Développeur        |
| Exécution des tests | pytest(cmd)        |
| Revue du plan | Trinôme (Partie 5) |
| Validation finale | Enseignant         |

