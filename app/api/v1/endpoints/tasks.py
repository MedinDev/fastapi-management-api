from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.repositories.task_repository import task_repository

router = APIRouter()

@router.get("/", response_model=List[Task])
async def read_tasks(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve tasks.
    """
    if current_user.role == "admin":
        tasks = await task_repository.get_multi(db, skip=skip, limit=limit)
    else:
        tasks = await task_repository.get_multi_by_owner(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return tasks

@router.post("/", response_model=Task)
async def create_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    task_in: TaskCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new task.
    """
    task = await task_repository.create_with_owner(
        db=db, obj_in=task_in, owner_id=current_user.id
    )
    return task

@router.get("/{id}", response_model=Task)
async def read_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get task by ID.
    """
    task = await task_repository.get(db=db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user.role != "admin" and (task.creator_id != current_user.id and task.assignee_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return task

@router.put("/{id}", response_model=Task)
async def update_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update task.
    """
    task = await task_repository.get(db=db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user.role != "admin" and (task.creator_id != current_user.id and task.assignee_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    task = await task_repository.update(db=db, db_obj=task, obj_in=task_in)
    return task

@router.delete("/{id}", response_model=Task)
async def delete_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete task.
    """
    task = await task_repository.get(db=db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user.role != "admin" and (task.creator_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    task = await task_repository.remove(db=db, id=id)
    return task
