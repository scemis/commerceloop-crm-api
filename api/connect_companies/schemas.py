from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from core.enums import StatusEnum

class CreateConnectCompanyRequest(BaseModel):
    company_id: int | None = None
    firm_name: str
    email: str
    phone: Optional[str] = None
    next_meeting: Optional[datetime] = None
    is_approved: bool
    status: StatusEnum = StatusEnum.pending
    description: Optional[str] = None
    last_update: Optional[datetime] = None
    class Config: from_attributes = True

class EditConnectCompanyRequest(BaseModel):
    next_meeting: Optional[datetime] = None
    is_approved: bool
    status: StatusEnum = StatusEnum.pending
    description: Optional[str] = None
    class Config: from_attributes = True

class ConnectCompanyOut(BaseModel):
    id: int
    worker_id: int
    company_id: int
    next_meeting: Optional[datetime] = None
    is_approved: Optional[bool] = None
    status: StatusEnum
    description: Optional[str] = None
    last_update: Optional[datetime] = None
    class Config: from_attributes = True
