from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.repositories.product_repository import product_repository

router = APIRouter()

@router.get("/", response_model=List[Product])
async def read_products(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve products.
    """
    if current_user.role == "admin":
        products = await product_repository.get_multi(db, skip=skip, limit=limit)
    else:
        products = await product_repository.get_multi_by_owner(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return products

@router.post("/", response_model=Product)
async def create_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    product_in: ProductCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new product.
    """
    product = await product_repository.create_with_owner(
        db=db, obj_in=product_in, owner_id=current_user.id
    )
    return product

@router.get("/{id}", response_model=Product)
async def read_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get product by ID.
    """
    product = await product_repository.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if current_user.role != "admin" and (product.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return product

@router.put("/{id}", response_model=Product)
async def update_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update product.
    """
    product = await product_repository.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if current_user.role != "admin" and (product.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    product = await product_repository.update(db=db, db_obj=product, obj_in=product_in)
    return product

@router.delete("/{id}", response_model=Product)
async def delete_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete product.
    """
    product = await product_repository.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if current_user.role != "admin" and (product.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    product = await product_repository.remove(db=db, id=id)
    return product
