# Notes de Version — FollowUp v1.0.0

**Date de release** : 25/02/2026

## Nouvelles fonctionnalités

- Module de gestion des incidents (CRUD complet)
- Soft delete avec traçabilité IEC 62304
- Gestion des suivis d'incidents (ajout, historique)
- Documentation API auto-générée via FastAPI (Swagger UI : `/docs`)
- Suite de tests unitaires et d'intégration (couverture > 80%)

## Problèmes connus

- `id_implant` et `id_processeur` non encore liés à la table `Incident`
- Le endpoint PUT ne valide pas les champs autorisés (correction prévue v1.1.0)
- Pas d'authentification JWT (prévu v1.2.0)

## Instructions de mise à jour
```bash
# 1. Récupérer les sources
git pull origin main

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Démarrer la base de données PostgreSQL via Docker
docker-compose up -d

# 4. Appliquer les migrations Alembic
alembic upgrade head

# 5. Lancer l'application
uvicorn src.main:app --reload

# 6. Lancer les tests
pytest
```

> **Note** : L'étape `docker-compose up -d` démarre le conteneur PostgreSQL en arrière-plan. 
> Vérifiez que Docker Desktop est lancé avant d'exécuter cette commande.
> Pour arrêter la base : `docker-compose down`