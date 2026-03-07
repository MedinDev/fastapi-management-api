from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.api import deps
from app.models.user import User
from app.models.product import Product
from app.models.task import Task

router = APIRouter()

@router.get("/stats", response_model=Dict[str, int])
async def get_stats(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get system statistics.
    """
    if current_user.role != "admin":
        # Return user specific stats
        products_count = await db.scalar(select(func.count(Product.id)).filter(Product.owner_id == current_user.id))
        tasks_count = await db.scalar(select(func.count(Task.id)).filter((Task.creator_id == current_user.id) | (Task.assignee_id == current_user.id)))
        return {
            "products": products_count or 0,
            "tasks": tasks_count or 0
        }
    
    # Admin stats
    users_count = await db.scalar(select(func.count(User.id)))
    products_count = await db.scalar(select(func.count(Product.id)))
    tasks_count = await db.scalar(select(func.count(Task.id)))
    
    return {
        "users": users_count or 0,
        "products": products_count or 0,
        "tasks": tasks_count or 0
    }
