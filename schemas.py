from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, time, datetime

# --- Employee Schemas ---
class EmployeeBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    role: Optional[str] = "employee"
    department: Optional[str] = None
    status: Optional[str] = "active"

class EmployeeCreate(EmployeeBase):
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class EmployeeResponse(EmployeeBase):
    id: int

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

# --- Task Schemas ---
class TaskBase(BaseModel):
    employee_id: int
    titre: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    statut: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[date] = None
    statut: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    employee: Optional[EmployeeResponse] = None

    class Config:
        from_attributes = True

# --- Conge (Leave) Schemas ---
class CongeBase(BaseModel):
    employee_id: int
    date_debut: date
    date_fin: date
    reason: Optional[str] = None
    statut: Optional[str] = None

class CongeCreate(CongeBase):
    pass

class CongeResponse(CongeBase):
    id: int
    employee: Optional[EmployeeResponse] = None

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

# --- Message Schemas ---
class MessageBase(BaseModel):
    content: str
    receiver_id: int

class MessageCreate(MessageBase):
    sender_id: int

class MessageResponse(MessageBase):
    id: int
    sender_id: int
    timestamp: datetime
    is_read: bool

    class Config:
        from_attributes = True

# --- Performance Schema ---
class PerformanceResponse(BaseModel):
    employee_id: int
    name: str
    department: Optional[str] = None
    tasks_completed: int
    total_tasks: int
    attendance_rate: float   # 0-100
    score: float             # 0-100

    class Config:
        from_attributes = True

# --- Task Stats Schema ---
class TaskStatsResponse(BaseModel):
    completed: int
    pending: int
    in_progress: int
    late: int
    total: int
    completion_rate: float   # 0-100

# --- Alert Schemas ---
class AlertItem(BaseModel):
    id: str                       # unique key for React
    severity: str                 # "danger" | "warning"
    alert_type: str               # "absenteeism" | "late_task" | "no_activity"
    employee_id: Optional[int] = None
    employee_name: Optional[str] = None
    message: str

class AlertsResponse(BaseModel):
    inactive_count: int
    employees: list[str]
