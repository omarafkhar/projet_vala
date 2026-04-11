from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import engine, get_db

# We don't automatically create tables here because it can crash 
# the app at startup if the database isn't running yet.
# tables already exist based on the schema.sql you have.
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Employee Management API",
    description="Backend API for the HR System",
    version="1.0.0"
)

# Allow React app (which usually runs on localhost:3000 or localhost:5173) to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production, e.g., ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Employee Management API. Visit /docs for the API documentation."}

# ==========================================
# EMPLOYEES ENDPOINTS
# ==========================================

@app.get("/employees", response_model=List[schemas.EmployeeResponse])
def get_employees(db: Session = Depends(get_db)):
    """Retrieve all employees."""
    return db.query(models.Employee).all()

@app.get("/employees/{id}", response_model=schemas.EmployeeResponse)
def get_employee(id: int, db: Session = Depends(get_db)):
    """Retrieve a specific employee by ID."""
    employee = db.query(models.Employee).filter(models.Employee.id == id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee

@app.post("/employees", response_model=schemas.EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    """Create a new employee."""
    # Check if email is already registered
    db_employee = db.query(models.Employee).filter(models.Employee.email == employee.email).first()
    if db_employee:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Using .model_dump() for Pydantic v2 compatibility
    new_employee = models.Employee(**employee.model_dump())
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@app.put("/employees/{id}", response_model=schemas.EmployeeResponse)
def update_employee(id: int, employee_update: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    """Update an existing employee."""
    employee = db.query(models.Employee).filter(models.Employee.id == id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    
    employee_data = employee_update.model_dump()
    for key, value in employee_data.items():
        setattr(employee, key, value)
        
    db.commit()
    db.refresh(employee)
    return employee

@app.delete("/employees/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(id: int, db: Session = Depends(get_db)):
    """Delete an employee and all their associated data (cascade)."""
    employee = db.query(models.Employee).filter(models.Employee.id == id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    
    db.delete(employee)
    db.commit()
    return None

# ==========================================
# TASKS ENDPOINTS
# ==========================================

@app.get("/employees/{id}/tasks", response_model=List[schemas.TaskResponse])
def get_employee_tasks(id: int, db: Session = Depends(get_db)):
    """Retrieve all tasks assigned to a specific employee."""
    employee = db.query(models.Employee).filter(models.Employee.id == id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee.tasks


@app.get("/tasks", response_model=List[schemas.TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    """Retrieve all tasks."""
    return db.query(models.Task).all()

@app.post("/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Create a new task assigned to an employee."""
    # Verify employee exists
    employee = db.query(models.Employee).filter(models.Employee.id == task.employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        
    new_task = models.Task(**task.model_dump())
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# ==========================================
# CONGES (LEAVES) ENDPOINTS
# ==========================================

@app.get("/conges", response_model=List[schemas.CongeResponse])
def get_conges(db: Session = Depends(get_db)):
    """Retrieve all leave requests (conges)."""
    return db.query(models.Conge).all()

@app.post("/conges", response_model=schemas.CongeResponse, status_code=status.HTTP_201_CREATED)
def create_conge(conge: schemas.CongeCreate, db: Session = Depends(get_db)):
    """Create a new leave request for an employee."""
    employee = db.query(models.Employee).filter(models.Employee.id == conge.employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        
    new_conge = models.Conge(**conge.model_dump())
    
    db.add(new_conge)
    db.commit()
    db.refresh(new_conge)
    return new_conge

# ==========================================
# PRESENCE ENDPOINTS
# ==========================================

@app.get("/presence", response_model=List[schemas.PresenceResponse])
def get_presences(db: Session = Depends(get_db)):
    """Retrieve all presence records."""
    return db.query(models.Presence).all()

@app.post("/presence", response_model=schemas.PresenceResponse, status_code=status.HTTP_201_CREATED)
def create_presence(presence: schemas.PresenceCreate, db: Session = Depends(get_db)):
    """Create a new presence record for an employee."""
    employee = db.query(models.Employee).filter(models.Employee.id == presence.employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        
    new_presence = models.Presence(**presence.model_dump())
    
    db.add(new_presence)
    db.commit()
    db.refresh(new_presence)
    return new_presence