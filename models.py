from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    telephone = Column(String(20))
    poste = Column(String(100))
    departement = Column(String(100))
    date_embauche = Column(Date)
    statut = Column(String(50))

    # Relationships to child tables
    tasks = relationship("Task", back_populates="employee", cascade="all, delete-orphan")
    conges = relationship("Conge", back_populates="employee", cascade="all, delete-orphan")
    presences = relationship("Presence", back_populates="employee", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"))
    titre = Column(String(200), nullable=False)
    description = Column(Text)
    deadline = Column(Date)
    statut = Column(String(50))

    employee = relationship("Employee", back_populates="tasks")


class Conge(Base):
    __tablename__ = "conges"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"))
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    statut = Column(String(50))

    employee = relationship("Employee", back_populates="conges")


class Presence(Base):
    __tablename__ = "presence"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    heure_entree = Column(Time)
    heure_sortie = Column(Time)
    statut = Column(String(50))

    employee = relationship("Employee", back_populates="presences")
