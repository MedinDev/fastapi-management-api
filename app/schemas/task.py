from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.task import TaskPriority, TaskStatus

class TaskBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    status: Optional[TaskStatus] = TaskStatus.TODO
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    title: str
    assignee_id: Optional[int] = None

class TaskUpdate(TaskBase):
    pass

class TaskInDBBase(TaskBase):
    id: int
    assignee_id: Optional[int] = None
    creator_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class Task(TaskInDBBase):
    pass
