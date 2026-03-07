from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.product import ProductStatus

class ProductBase(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = 0
    sku: Optional[str] = None
    status: Optional[ProductStatus] = ProductStatus.DRAFT

class ProductCreate(ProductBase):
    name: str
    slug: str
    price: float

class ProductUpdate(ProductBase):
    pass

class ProductInDBBase(ProductBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class Product(ProductInDBBase):
    pass
