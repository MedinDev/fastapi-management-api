from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.base import CRUDBase
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: TaskCreate, owner_id: int
    ) -> Task:
        obj_in_data = obj_in.model_dump()
        # Task usually has creator_id and assignee_id.
        # Assuming creator is the current user. Assignee might be in obj_in or default to creator.
        # TaskCreate schema: title (required), others optional.
        # Task model: assignee_id, creator_id.
        
        db_obj = self.model(**obj_in_data, creator_id=owner_id)
        # If assignee_id is not provided, maybe assign to creator?
        if not db_obj.assignee_id:
             db_obj.assignee_id = owner_id
             
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_by_owner(
        self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        # Get tasks where user is creator OR assignee
        result = await db.execute(
            select(self.model)
            .filter((self.model.creator_id == owner_id) | (self.model.assignee_id == owner_id))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

task_repository = CRUDTask(Task)
