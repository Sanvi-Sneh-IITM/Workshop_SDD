from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from database import TaskStatus

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Project schemas
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Task schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    project_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None

class TaskSummary(TaskBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Task(TaskBase):
    id: int
    project_id: int
    created_at: datetime
    subtasks: List["Subtask"] = []

    class Config:
        from_attributes = True

# Subtask schemas
class SubtaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO

class SubtaskCreate(SubtaskBase):
    pass

class SubtaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

class Subtask(SubtaskBase):
    id: int
    task_id: int
    created_at: datetime

    class Config:
        from_attributes = True

Task.model_rebuild()

# Comment schemas
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    task_id: int

class Comment(CommentBase):
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token schema
class Token(BaseModel):
    access_token: str
    token_type: str
