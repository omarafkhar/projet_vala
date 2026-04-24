from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel
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

@app.on_event("startup")
def startup_event():
    # No auto-seeding – users are seeded via reset_db.sql with plain-text passwords.
    pass

@app.get("/")
def read_root():
    return {"message": "Welcome to the Employee Management API. Visit /docs for the API documentation."}

# ==========================================
# AUTH ENDPOINTS
# ==========================================



@app.post("/login", response_model=schemas.LoginResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user with plain-text password comparison."""
    print(f"DEBUG: request received for email: {request.email}")
    
    # 1. Find user by email
    user = db.query(models.Employee).filter(models.Employee.email == request.email).first()

    # 2. User not found
    if not user:
        print("DEBUG: user not found in database.")
        raise HTTPException(
            status_code=400,
            detail="Invalid email or password"
        )
    print(f"DEBUG: user found: {user.email}")

    # 3. Plain-text comparison (passwords stored as plain text in DB)
    if request.password != user.password:
        print("DEBUG: password match failed.")
        raise HTTPException(
            status_code=400,
            detail="Invalid email or password"
        )
    print("DEBUG: password match success.")

    # 4. Return user info
    return schemas.LoginResponse(id=user.id, email=user.email, role=user.role)

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
    emp_data = employee.model_dump(exclude={"password"})
    
    new_employee = models.Employee(**emp_data, password=employee.password)
    
    if not new_employee.role:
        new_employee.role = "employee"
        
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
    
    employee_data = employee_update.model_dump(exclude={"password"})
    for key, value in employee_data.items():
        setattr(employee, key, value)
        
    if employee_update.password:
        employee.password = employee_update.password
        
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
# EMPLOYEE PROFILE ENDPOINT
# ==========================================

@app.get("/employees/{id}/profile")
def get_employee_profile(id: int, db: Session = Depends(get_db)):
    """Return a full profile bundle for one employee: info, tasks, presence, messages, performance."""
    from sqlalchemy import or_
    employee = db.query(models.Employee).filter(models.Employee.id == id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    # Tasks
    tasks_data = [
        {
            "id": t.id,
            "titre": t.titre,
            "description": t.description,
            "statut": t.statut,
            "deadline": str(t.deadline) if t.deadline else None,
        }
        for t in (employee.tasks or [])
    ]

    # Presence
    presence_data = [
        {
            "id": p.id,
            "date": str(p.date),
            "heure_entree": str(p.heure_entree) if p.heure_entree else None,
            "heure_sortie": str(p.heure_sortie) if p.heure_sortie else None,
            "statut": p.statut,
        }
        for p in sorted(employee.presences or [], key=lambda x: x.date, reverse=True)
    ]

    # Messages (conversations involving this employee)
    messages_raw = db.query(models.Message).filter(
        or_(models.Message.sender_id == id, models.Message.receiver_id == id)
    ).order_by(models.Message.timestamp.desc()).limit(20).all()

    messages_data = []
    for m in messages_raw:
        sender_name = f"{m.sender.prenom} {m.sender.nom}" if m.sender else "Unknown"
        receiver_name = f"{m.receiver.prenom} {m.receiver.nom}" if m.receiver else "Unknown"
        messages_data.append({
            "id": m.id,
            "content": m.content,
            "sender_id": m.sender_id,
            "sender_name": sender_name,
            "receiver_id": m.receiver_id,
            "receiver_name": receiver_name,
            "timestamp": m.timestamp.isoformat() if m.timestamp else None,
            "is_read": m.is_read,
        })

    # Performance
    perf = _compute_performance(employee)

    return {
        "id": employee.id,
        "nom": employee.nom,
        "prenom": employee.prenom,
        "email": employee.email,
        "role": employee.role,
        "department": employee.department,
        "status": employee.status,
        "tasks": tasks_data,
        "presence": presence_data,
        "messages": messages_data,
        "performance": {
            "score": perf.score,
            "tasks_completed": perf.tasks_completed,
            "total_tasks": perf.total_tasks,
            "attendance_rate": perf.attendance_rate,
        },
    }

# ==========================================
# TASKS ENDPOINTS
# ==========================================

@app.get("/tasks/employee/{employee_id}", response_model=List[schemas.TaskResponse])
def get_tasks_by_employee_id(employee_id: int, db: Session = Depends(get_db)):
    """Retrieve all tasks assigned to a specific employee (alias)."""
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee.tasks

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

@app.get("/tasks/stats", response_model=schemas.TaskStatsResponse)
def get_task_stats(db: Session = Depends(get_db)):
    """Return aggregate task analytics: completed, pending, in_progress, late, total, completion_rate."""
    from datetime import date as date_type
    tasks = db.query(models.Task).all()
    today = date_type.today()

    completed_statuses  = {"terminé", "termine", "done", "completed"}
    inprogress_statuses = {"en cours", "in progress", "in_progress"}
    pending_statuses    = {"a faire", "à faire", "todo", "pending", "to do"}

    completed   = 0
    in_progress = 0
    pending     = 0
    late        = 0

    for t in tasks:
        raw = (t.statut or "").strip().lower()
        is_done = raw in completed_statuses

        if is_done:
            completed += 1
        elif raw in inprogress_statuses:
            in_progress += 1
            # still counts as late if deadline passed and not finished
            if t.deadline and t.deadline < today:
                late += 1
        else:
            pending += 1
            if t.deadline and t.deadline < today:
                late += 1

    total = len(tasks)
    completion_rate = round((completed / total * 100) if total > 0 else 0.0, 1)

    return schemas.TaskStatsResponse(
        completed=completed,
        pending=pending,
        in_progress=in_progress,
        late=late,
        total=total,
        completion_rate=completion_rate,
    )

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

@app.put("/tasks/{id}", response_model=schemas.TaskResponse)
def update_task(id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Update an existing task."""
    task = db.query(models.Task).filter(models.Task.id == id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    task_data = task_update.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)
        
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int, db: Session = Depends(get_db)):
    """Delete a task."""
    task = db.query(models.Task).filter(models.Task.id == id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return None

# ==========================================
# CONGES (LEAVES) ENDPOINTS
# ==========================================

@app.get("/conges", response_model=List[schemas.CongeResponse])
def get_conges(db: Session = Depends(get_db)):
    """Retrieve all leave requests (conges)."""
    return db.query(models.Conge).all()

@app.get("/conges/employee/{employee_id}", response_model=List[schemas.CongeResponse])
def get_employee_conges(employee_id: int, db: Session = Depends(get_db)):
    """Retrieve leave requests for a specific employee."""
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee.conges

@app.post("/conges", response_model=schemas.CongeResponse, status_code=status.HTTP_201_CREATED)
def create_conge(conge: schemas.CongeCreate, db: Session = Depends(get_db)):
    """Create a new leave request for an employee."""
    employee = db.query(models.Employee).filter(models.Employee.id == conge.employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        
    conge_data = conge.model_dump()
    if not conge_data.get("statut"):
        conge_data["statut"] = "pending"
        
    new_conge = models.Conge(**conge_data)
    
    db.add(new_conge)
    db.commit()
    db.refresh(new_conge)
    return new_conge

@app.put("/conges/{id}/approve", response_model=schemas.CongeResponse)
def approve_conge(id: int, db: Session = Depends(get_db)):
    """Approve a leave request."""
    conge = db.query(models.Conge).filter(models.Conge.id == id).first()
    if not conge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conge not found")
    
    conge.statut = "approved"
    db.commit()
    db.refresh(conge)
    return conge

@app.put("/conges/{id}/reject", response_model=schemas.CongeResponse)
def reject_conge(id: int, db: Session = Depends(get_db)):
    """Reject a leave request."""
    conge = db.query(models.Conge).filter(models.Conge.id == id).first()
    if not conge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conge not found")
    
    conge.statut = "rejected"
    db.commit()
    db.refresh(conge)
    return conge

# ==========================================
# PRESENCE ENDPOINTS
# ==========================================

class PresenceAction(BaseModel):
    employee_id: int

@app.post("/presence/check-in", response_model=schemas.PresenceResponse)
def check_in(action: PresenceAction, db: Session = Depends(get_db)):
    """Employee check-in for today."""
    now = datetime.now()
    existing = db.query(models.Presence).filter(
        models.Presence.employee_id == action.employee_id,
        models.Presence.date == now.date()
    ).first()
    
    if existing:
        return existing
        
    presence = models.Presence(
        employee_id=action.employee_id,
        date=now.date(),
        heure_entree=now.time(),
        statut="Present"
    )
    db.add(presence)
    db.commit()
    db.refresh(presence)
    return presence

@app.post("/presence/check-out", response_model=schemas.PresenceResponse)
def check_out(action: PresenceAction, db: Session = Depends(get_db)):
    """Employee check-out for today."""
    now = datetime.now()
    existing = db.query(models.Presence).filter(
        models.Presence.employee_id == action.employee_id,
        models.Presence.date == now.date()
    ).first()
    
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No check-in found for today")
        
    existing.heure_sortie = now.time()
    db.commit()
    db.refresh(existing)
    return existing

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

# ==========================================
# MESSAGES ENDPOINTS
# ==========================================

@app.get("/messages/{user_id}", response_model=List[schemas.MessageResponse])
def get_user_messages(user_id: int, db: Session = Depends(get_db)):
    """Retrieve all messages where the user is either sender or receiver."""
    print(f"DEBUG: messages fetched for user {user_id}")
    from sqlalchemy import or_
    messages = db.query(models.Message).filter(
        or_(
            models.Message.sender_id == user_id,
            models.Message.receiver_id == user_id
        )
    ).order_by(models.Message.timestamp.asc()).all()
    print(f"DEBUG: retrieved {len(messages)} messages for user {user_id}")
    return messages

@app.post("/messages", response_model=schemas.MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    """Send a new message."""
    print(f"DEBUG: message sent from {message.sender_id} to {message.receiver_id} content: {message.content}")
    new_message = models.Message(**message.model_dump())
    db.add(new_message)
    try:
        db.commit()
        db.refresh(new_message)
        print("DEBUG: message successfully saved to database")
        return new_message
    except Exception as e:
        db.rollback()
        print(f"DEBUG: Error saving message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save message")

@app.put("/messages/{message_id}/read", response_model=schemas.MessageResponse)
def mark_message_as_read(message_id: int, db: Session = Depends(get_db)):
    """Mark a message as read."""
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    
    message.is_read = True
    db.commit()
    db.refresh(message)
    return message

# ==========================================
# PERFORMANCE ENDPOINTS
# ==========================================

def _compute_performance(employee: models.Employee) -> schemas.PerformanceResponse:
    """Helper: compute performance metrics for a single employee."""
    # Tasks
    all_tasks = employee.tasks or []
    total_tasks = len(all_tasks)
    tasks_completed = sum(1 for t in all_tasks if t.statut and t.statut.lower() in ("terminé", "termine", "done", "completed"))

    # Attendance – use presence records as a proxy for working days recorded
    all_presences = employee.presences or []
    total_presences = len(all_presences)
    present_days = sum(1 for p in all_presences if p.statut and p.statut.lower() in ("present", "présent"))
    attendance_rate = round((present_days / total_presences * 100) if total_presences > 0 else 0.0, 1)

    # Score: 60 % weight on task completion + 40 % weight on attendance
    task_ratio = (tasks_completed / total_tasks) if total_tasks > 0 else 0.0
    attendance_ratio = attendance_rate / 100.0
    score = round((task_ratio * 60 + attendance_ratio * 40), 1)

    full_name = f"{employee.prenom} {employee.nom}"
    return schemas.PerformanceResponse(
        employee_id=employee.id,
        name=full_name,
        department=employee.department,
        tasks_completed=tasks_completed,
        total_tasks=total_tasks,
        attendance_rate=attendance_rate,
        score=score,
    )


@app.get("/performance", response_model=List[schemas.PerformanceResponse])
def get_all_performance(db: Session = Depends(get_db)):
    """Return performance metrics for every employee, sorted by score descending."""
    employees = db.query(models.Employee).filter(models.Employee.role == "employee").all()
    results = [_compute_performance(emp) for emp in employees]
    results.sort(key=lambda r: r.score, reverse=True)
    return results


@app.get("/performance/{employee_id}", response_model=schemas.PerformanceResponse)
def get_employee_performance(employee_id: int, db: Session = Depends(get_db)):
    """Return performance metrics for a specific employee."""
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return _compute_performance(employee)

# ==========================================
# GLOBAL SEARCH ENDPOINT
# ==========================================

@app.get("/search")
def global_search(q: str = "", db: Session = Depends(get_db)):
    """
    Global search across employees, tasks, and messages.
    Returns grouped results matching the query string (case-insensitive).
    """
    if not q or len(q.strip()) < 1:
        return {"employees": [], "tasks": [], "messages": [], "total": 0}

    term = q.strip().lower()

    # ── Employees ──────────────────────────────────────────────────
    all_employees = db.query(models.Employee).all()
    matched_employees = []
    for emp in all_employees:
        full_name = f"{emp.prenom} {emp.nom}".lower()
        haystack = " ".join(filter(None, [
            full_name,
            (emp.email or "").lower(),
            (emp.department or "").lower(),
            (emp.role or "").lower(),
        ]))
        if term in haystack:
            matched_employees.append({
                "id": emp.id,
                "type": "employee",
                "title": f"{emp.prenom} {emp.nom}",
                "subtitle": emp.email,
                "meta": emp.department or emp.role,
                "url": "/",
            })

    # ── Tasks ───────────────────────────────────────────────────────
    all_tasks = db.query(models.Task).all()
    matched_tasks = []
    for task in all_tasks:
        employee_name = ""
        if task.employee:
            employee_name = f"{task.employee.prenom} {task.employee.nom}".lower()
        haystack = " ".join(filter(None, [
            (task.titre or "").lower(),
            (task.description or "").lower(),
            (task.statut or "").lower(),
            employee_name,
        ]))
        if term in haystack:
            matched_tasks.append({
                "id": task.id,
                "type": "task",
                "title": task.titre,
                "subtitle": f"Assigned to {task.employee.prenom} {task.employee.nom}" if task.employee else "Unassigned",
                "meta": task.statut or "No status",
                "url": "/tasks",
            })

    # ── Messages ────────────────────────────────────────────────────
    all_messages = db.query(models.Message).all()
    matched_messages = []
    for msg in all_messages:
        sender_name = f"{msg.sender.prenom} {msg.sender.nom}" if msg.sender else "Unknown"
        receiver_name = f"{msg.receiver.prenom} {msg.receiver.nom}" if msg.receiver else "Unknown"
        haystack = " ".join(filter(None, [
            (msg.content or "").lower(),
            sender_name.lower(),
            receiver_name.lower(),
        ]))
        if term in haystack:
            preview = (msg.content or "")[:80] + ("…" if len(msg.content or "") > 80 else "")
            matched_messages.append({
                "id": msg.id,
                "type": "message",
                "title": preview,
                "subtitle": f"{sender_name} → {receiver_name}",
                "meta": msg.timestamp.strftime("%Y-%m-%d %H:%M") if msg.timestamp else "",
                "url": "/messages",
            })

    total = len(matched_employees) + len(matched_tasks) + len(matched_messages)
    return {
        "employees": matched_employees[:10],
        "tasks": matched_tasks[:10],
        "messages": matched_messages[:10],
        "total": total,
    }

# ==========================================
# ALERTS ENDPOINT
# ==========================================

@app.get("/alerts", response_model=schemas.AlertsResponse)
def get_alerts(db: Session = Depends(get_db)):
    """
    Return grouped inactive employees.
    """
    employees = db.query(models.Employee).filter(models.Employee.role == "employee").all()

    inactive_employees = []

    for emp in employees:
        has_tasks = bool(emp.tasks)
        has_presences = bool(emp.presences)
        if not has_tasks and not has_presences:
            inactive_employees.append(f"{emp.prenom} {emp.nom}")

    return schemas.AlertsResponse(
        inactive_count=len(inactive_employees),
        employees=inactive_employees
    )