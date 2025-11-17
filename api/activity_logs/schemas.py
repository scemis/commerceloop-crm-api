from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from core.enums import ActivityLogEnum, EntityEnum

class ActivityLogCreate(BaseModel):
    action: ActivityLogEnum
    description: Optional[str] = None
    entity: EntityEnum
    emploee_id: int
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class ActivityLogOut(BaseModel):
    id: int
    action: ActivityLogEnum
    description: Optional[str] = None
    entity: EntityEnum
    created_at: datetime
    emploee_id: int
    user_id: Optional[int] = None

    class Config:
        from_attributes = True