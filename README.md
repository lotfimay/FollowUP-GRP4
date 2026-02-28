# FollowUp — Module de Gestion des Incidents

Application de suivi médical pour patients porteurs d'implants cochléaires.  
Développée dans le cadre du cours **Développement d'Applications de Gestion de Santé** — Polytech Lyon / Lyon 1.

---

## Stack technique

- **Backend** : Python 3.12 + FastAPI
- **Base de données** : PostgreSQL (via Docker)
- **ORM** : SQLAlchemy (async)
- **Migrations** : Alembic
- **Tests** : pytest + pytest-asyncio + httpx
- **Couverture** : pytest-cov

---

## Installation

### Prérequis

- Python 3.12+
- Docker Desktop

### Étapes

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd FollowUP-GRP4

# 2. Créer et activer l'environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Démarrer la base de données
docker-compose up -d

# 5. Appliquer les migrations
alembic upgrade head

# 6. Lancer l'application
uvicorn src.main:app --reload
```

L'API est accessible sur `http://localhost:8000`.  
La documentation Swagger est disponible sur `http://localhost:8000/docs`.

---

## Tests

```bash
# Lancer tous les tests avec couverture
pytest

# Rapport de couverture HTML
# Généré automatiquement dans coverage_html/index.html
```

Couverture actuelle : **~95%** (objectif IEC 62304 Classe B : ≥ 80%)

---

## Endpoints principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/incidents/` | Créer un incident |
| GET | `/api/incidents/{id}` | Récupérer un incident |
| GET | `/api/incidents/patient/{id}` | Incidents d'un patient |
| PUT | `/api/incidents/{id}` | Mettre à jour un incident |
| DELETE | `/api/incidents/{id}` | Supprimer (soft delete) |
| POST | `/api/incidents/{id}/suivis` | Ajouter un suivi |
| GET | `/api/incidents/{id}/suivis` | Historique des suivis |

---

## Structure du projet

```
FollowUP-GRP4/
├── src/
│   ├── incidents/
│   │   ├── router.py       # Endpoints REST
│   │   ├── schemas.py      # Validation Pydantic
│   │   └── service.py      # Logique métier
│   ├── database.py         # Connexion async PostgreSQL
│   ├── models.py           # Modèles SQLAlchemy
│   └── main.py             # Point d'entrée FastAPI
├── tests/
│   ├── conftest.py         # Fixtures (SQLite en mémoire)
│   ├── test_unit.py        # Tests unitaires
│   └── test_integration.py # Tests d'intégration REST
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── openapi.yaml
```

---

## Conformité IEC 62304

Ce module est classé **Classe B** (blessure possible sans risque vital).  
Les exigences suivantes sont respectées :

- Soft delete pour la traçabilité des données
- Couverture de code ≥ 80%
- Plan de tests et rapport de tests documentés
- Revue de code par binôme

---

## Arrêter l'application

```bash
# Arrêter le serveur : Ctrl+C

# Arrêter la base de données
docker-compose down
```
