from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="employee")
    department = Column(String(100), nullable=True)
    status = Column(String(50), default="active")

    # Relationships to child tables
    tasks = relationship("Task", back_populates="employee", cascade="all, delete-orphan")
    conges = relationship("Conge", back_populates="employee", cascade="all, delete-orphan")
    presences = relationship("Presence", back_populates="employee", cascade="all, delete-orphan")
    
    # Message relationships
    sent_messages = relationship("Message", foreign_keys="[Message.sender_id]", back_populates="sender", cascade="all, delete-orphan")
    received_messages = relationship("Message", foreign_keys="[Message.receiver_id]", back_populates="receiver", cascade="all, delete-orphan")


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
    reason = Column(Text, nullable=True)
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

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    sender = relationship("Employee", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("Employee", foreign_keys=[receiver_id], back_populates="received_messages")
