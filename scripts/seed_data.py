import asyncio
import sys
import os
from datetime import datetime

# Ajout de la racine du projet au PATH pour importer 'src'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models import Medecin, Patient, Processeur, Implant, Incident, SuiviIncident

async def seed():
    async with AsyncSessionLocal() as db:
        # Vérification d'idempotence
        result = await db.execute(select(Patient))
        if result.scalars().first():
            print("La base de données contient déjà des données.")
            return

        print("Début du peuplement de la base de données...")

        # 1. Insertion des Médecins
        medecins = [
            Medecin(id=1, nom="Leclerc", prenom="Marie", specialite="ORL"),
            Medecin(id=2, nom="Durand", prenom="Paul", specialite="Audiologue")
        ]
        
        # 2. Insertion des Patients
        patients = [
            Patient(id=1, nom="Dupont", prenom="Jean", date_naissance=datetime(1980, 5, 12), sexe="Masculin", adresse="123 Rue de Paris"),
            Patient(id=2, nom="Martin", prenom="Sophie", date_naissance=datetime(1975, 9, 24), sexe="Féminin", adresse="45 Avenue des Champs")
        ]
        
        # 3. Insertion des Implants (Doivent être insérés AVANT les processeurs à cause de la FK)
        implants = [
            Implant(id=1, type_implant="Advanced-Bionics", date_pose=datetime(2023, 1, 15), nombre_electrodes=22, id_patient=1),
            Implant(id=2, type_implant="Cochlear", date_pose=datetime(2022, 11, 10), nombre_electrodes=16, id_patient=2)
        ]
        
        # 4. Insertion des Processeurs (Liés aux implants)
        processeurs = [
            Processeur(id=1, type_processeur="Processeur A", date_installation=datetime(2023, 1, 15), batterie="Rechargeable", id_implant=1),
            Processeur(id=2, type_processeur="Processeur B", date_installation=datetime(2022, 11, 10), batterie="Piles", id_implant=2)
        ]
        
        # 5. Insertion des Incidents
        incidents = [
            Incident(id=1, date_incident=datetime(2023, 3, 20), heure_incident=datetime(2023, 3, 20, 14, 30), gravite="Mineur", 
                     description="Son faible après calibration", id_patient=1, id_medecin=1),
            Incident(id=2, date_incident=datetime(2022, 12, 1), heure_incident=datetime(2022, 12, 1, 10, 15), gravite="Modéré", 
                     description="Processeur défectueux", id_patient=2, id_medecin=2)
        ]
        
        # 6. Insertion des Suivis
        suivis = [
            SuiviIncident(id=1, date_suivi=datetime(2023, 3, 25), actions_prises="Ajustement du processeur", id_incident=1, id_medecin=1),
            SuiviIncident(id=2, date_suivi=datetime(2022, 12, 5), actions_prises="Remplacement du processeur", id_incident=2, id_medecin=2)
        ]

        # Ordre critique respecté : Medecins, Patients, Implants, Processeurs, Incidents, Suivis
        db.add_all(medecins + patients + implants + processeurs + incidents + suivis)
        await db.commit()
        print("Base de données peuplée avec succès !")

if __name__ == "__main__":
    asyncio.run(seed())