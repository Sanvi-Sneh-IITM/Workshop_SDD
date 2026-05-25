from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import timedelta

import schemas
from database import get_db, init_db, User, Project, Task, Comment, Subtask, TaskStatus
from auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="Task Manager API", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Auth endpoints
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Project endpoints
@app.post("/projects", response_model=schemas.Project)
def create_project(
    project: schemas.ProjectCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_project = Project(**project.dict(), owner_id=current_user.id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@app.get("/projects", response_model=List[schemas.Project])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Project).filter(Project.owner_id == current_user.id).all()

@app.get("/projects/{project_id}", response_model=schemas.Project)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}

def get_owned_task(task_id: int, db: Session, current_user: User) -> Task:
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Task endpoints
@app.post("/tasks", response_model=schemas.TaskSummary)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify project belongs to user
    project = db.query(Project).filter(
        Project.id == task.project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_task = Task(**task.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/tasks", response_model=List[schemas.TaskSummary])
def list_tasks(
    project_id: int = None,
    status: TaskStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Task).join(Project).filter(Project.owner_id == current_user.id)
    
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == status)
    
    return query.all()

@app.get("/tasks/{task_id}", response_model=schemas.Task)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = (
        db.query(Task)
        .options(joinedload(Task.subtasks))
        .join(Project)
        .filter(Task.id == task_id, Project.owner_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.subtasks.sort(key=lambda s: s.created_at)
    return task

@app.put("/tasks/{task_id}", response_model=schemas.TaskSummary)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}

# Comment endpoints
@app.post("/comments", response_model=schemas.Comment)
def create_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify task belongs to user's project
    task = db.query(Task).join(Project).filter(
        Task.id == comment.task_id,
        Project.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    new_comment = Comment(**comment.dict(), user_id=current_user.id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@app.get("/tasks/{task_id}/comments", response_model=List[schemas.Comment])
def list_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify task belongs to user
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return db.query(Comment).filter(Comment.task_id == task_id).all()

# Subtask endpoints
@app.post("/tasks/{task_id}/subtasks", response_model=schemas.Subtask, status_code=status.HTTP_201_CREATED)
def create_subtask(
    task_id: int,
    subtask: schemas.SubtaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_owned_task(task_id, db, current_user)
    new_subtask = Subtask(**subtask.dict(), task_id=task_id)
    db.add(new_subtask)
    db.commit()
    db.refresh(new_subtask)
    return new_subtask

@app.get("/tasks/{task_id}/subtasks", response_model=List[schemas.Subtask])
def list_subtasks(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_owned_task(task_id, db, current_user)
    return (
        db.query(Subtask)
        .filter(Subtask.task_id == task_id)
        .order_by(Subtask.created_at.asc())
        .all()
    )

@app.get("/tasks/{task_id}/subtasks/{subtask_id}", response_model=schemas.Subtask)
def get_subtask(
    task_id: int,
    subtask_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_owned_task(task_id, db, current_user)
    subtask = db.query(Subtask).filter(
        Subtask.id == subtask_id,
        Subtask.task_id == task_id
    ).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return subtask

@app.put("/tasks/{task_id}/subtasks/{subtask_id}", response_model=schemas.Subtask)
def update_subtask(
    task_id: int,
    subtask_id: int,
    subtask_update: schemas.SubtaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_owned_task(task_id, db, current_user)
    subtask = db.query(Subtask).filter(
        Subtask.id == subtask_id,
        Subtask.task_id == task_id
    ).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    update_data = subtask_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subtask, field, value)

    db.commit()
    db.refresh(subtask)
    return subtask

@app.delete("/tasks/{task_id}/subtasks/{subtask_id}")
def delete_subtask(
    task_id: int,
    subtask_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_owned_task(task_id, db, current_user)
    subtask = db.query(Subtask).filter(
        Subtask.id == subtask_id,
        Subtask.task_id == task_id
    ).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    db.delete(subtask)
    db.commit()
    return {"message": "Subtask deleted"}

@app.get("/")
def root():
    return {"message": "Task Manager API", "docs": "/docs"}
