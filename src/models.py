from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
import enum
from src.database import Base

class StatutIncident(str, enum.Enum):
    OUVERT = "Ouvert"
    EN_COURS = "EnCours"
    RESOLU = "Resolu"
    FERME = "Ferme"

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    date_naissance = Column(DateTime, nullable=False)
    sexe = Column(String(10), nullable=False)
    adresse = Column(String(255))
    telephone = Column(String(20))
    email = Column(String(100))
    
    implants = relationship("Implant", back_populates="patient")
    incidents = relationship("Incident", back_populates="patient")

class Implant(Base):
    __tablename__ = "implants"
    
    id = Column(Integer, primary_key=True)
    type_implant = Column(String(100), nullable=False)
    date_pose = Column(DateTime, nullable=False)
    nombre_electrodes = Column(Integer, nullable=False)
    id_patient = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    patient = relationship("Patient", back_populates="implants")
    processeur = relationship("Processeur", back_populates="implant", uselist=False)

class Processeur(Base):
    __tablename__ = "processeurs"
    
    id = Column(Integer, primary_key=True)
    type_processeur = Column(String(100), nullable=False)
    date_installation = Column(DateTime, nullable=False)
    batterie = Column(String(50))
    id_implant = Column(Integer, ForeignKey("implants.id"), nullable=False)
    
    implant = relationship("Implant", back_populates="processeur")

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True)
    date_incident = Column(DateTime, nullable=False)
    heure_incident = Column(DateTime, nullable=False)
    gravite = Column(String(50), nullable=False)
    description = Column(String(2000), nullable=False)
    statut = Column(Enum(StatutIncident), default=StatutIncident.OUVERT)
    
    id_patient = Column(Integer, ForeignKey("patients.id"), nullable=False)
    id_medecin = Column(Integer, nullable=True)
    
    patient = relationship("Patient", back_populates="incidents")
    suivis = relationship("SuiviIncident", back_populates="incident")

class SuiviIncident(Base):
    __tablename__ = "suivi_incidents"
    
    id = Column(Integer, primary_key=True)
    date_suivi = Column(DateTime, nullable=False, default=func.now())
    actions_prises = Column(String(2000), nullable=False)
    
    id_incident = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    id_medecin = Column(Integer, ForeignKey("medecins.id"), nullable=False)
    
    incident = relationship("Incident", back_populates="suivis")

class Medecin(Base):
    __tablename__ = "medecins"
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    specialite = Column(String(100), nullable=False)

class RendezVous(Base):
    __tablename__ = "rendezvous"
    
    id = Column(Integer, primary_key=True)
    date_rendezvous = Column(DateTime, nullable=False)
    motif = Column(String(255), nullable=False)
    id_patient = Column(Integer, ForeignKey("patients.id"), nullable=False)
    id_medecin = Column(Integer, ForeignKey("medecins.id"), nullable=False)

class SuiviReglage(Base):
    __tablename__ = "suivireglage"
    
    id = Column(Integer, primary_key=True)
    date_reglage = Column(DateTime, nullable=False)
    type_reglage = Column(String(100), nullable=False)
    resultat_reglage = Column(String(255), nullable=False)
    id_patient = Column(Integer, ForeignKey("patients.id"), nullable=False)
    id_medecin = Column(Integer, ForeignKey("medecins.id"), nullable=False)