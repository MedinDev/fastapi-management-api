from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.base import CRUDBase
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: ProductCreate, owner_id: int
    ) -> Product:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
        
    async def get_multi_by_owner(
        self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        result = await db.execute(
            select(self.model)
            .filter(self.model.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

product_repository = CRUDProduct(Product)
