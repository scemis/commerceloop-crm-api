from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CompanyBase(BaseModel):
    firm_name: str
    email: str
    phone: Optional[str] = None
    created_at: datetime
    class Config: from_attributes = True
