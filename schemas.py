from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, time

# --- Employee Schemas ---
class EmployeeBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    telephone: Optional[str] = None
    poste: Optional[str] = None
    departement: Optional[str] = None
    date_embauche: Optional[date] = None
    statut: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int

    class Config:
        from_attributes = True

# --- Task Schemas ---
class TaskBase(BaseModel):
    employee_id: int
    titre: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    statut: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int

    class Config:
        from_attributes = True

# --- Conge (Leave) Schemas ---
class CongeBase(BaseModel):
    employee_id: int
    date_debut: date
    date_fin: date
    statut: Optional[str] = None

class CongeCreate(CongeBase):
    pass

class CongeResponse(CongeBase):
    id: int

    class Config:
        from_attributes = True

# --- Presence Schemas ---
class PresenceBase(BaseModel):
    employee_id: int
    date: date
    heure_entree: Optional[time] = None
    heure_sortie: Optional[time] = None
    statut: Optional[str] = None

class PresenceCreate(PresenceBase):
    pass

class PresenceResponse(PresenceBase):
    id: int

    class Config:
        from_attributes = True
