from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SearchUserRequest(BaseModel):
    userId: int | None = None
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    created_at: datetime
    description: Optional[str] = None
    last_date_connection: Optional[datetime] = None
    role: str
    country: Optional[str] = None
    city: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    class Config: from_attributes = True

class EditUserRequest(BaseModel):
    first_name: str = Field(default=None)
    last_name: str
    email: str
    phone: Optional[str] = None
    description: Optional[str] = None
    role_id: int
    country: Optional[str] = None
    city: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    class Config: from_attributes = True
