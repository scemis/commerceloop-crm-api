from pydantic import BaseModel
from typing import Optional

class CategoryCreate(BaseModel):
    name: str
    class Config: from_attributes = True

class CategoryOut(BaseModel):
    id: int
    name: str
    class Config: from_attributes = True

class SubCategoryCreate(BaseModel):
    name: str
    count: int
    length: int
    width: int
    height: int
    price_per_piece: float
    category_id: int
    booked: Optional[int] = None
    class Config: from_attributes = True

class SubCategoryUpdate(BaseModel):
    name: str
    count: int
    length: int
    width: int
    height: int
    price_per_piece: float
    booked: Optional[int] = None
    class Config: from_attributes = True

class SubCategoryOut(BaseModel):
    id: int
    name: str
    count: Optional[int] = None
    booked: Optional[int] = 0
    length: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    price_per_piece: Optional[float] = None
    category_id: Optional[int] = None
    balance: Optional[int] = None
    m3: Optional[float] = None
    class Config: from_attributes = True
