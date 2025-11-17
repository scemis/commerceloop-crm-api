from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from core.enums import StatusEnum
from api.categories.schemas import CategoryOut, SubCategoryOut

class ProductCreate(BaseModel):
    customer_name: str
    count: int
    length: int
    width: int
    height: int
    total_price: Optional[float] = None
    description: Optional[str] = None
    category_id: int
    sub_category_id: int
    class Config: from_attributes = True

class ProductOut(BaseModel):
    id: int
    customer_name: str
    count: int
    length: int
    width: int
    height: int
    total_price: Optional[float] = None
    description: Optional[str] = None
    created_at: datetime
    last_update: Optional[datetime] = None
    status: StatusEnum
    category_id: int
    sub_category_id: int
    category_obj: Optional[CategoryOut] = None
    sub_category_obj: Optional[SubCategoryOut] = None
    class Config: from_attributes = True
