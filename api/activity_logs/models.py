from sqlalchemy import Column, Integer, Enum, Text, ForeignKey
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from core.db import Base
from core.enums import ActivityLogEnum, EntityEnum

class ActivityLogs(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(Enum(ActivityLogEnum, name="activity_action"), nullable=False)
    description = Column(Text, nullable=True)
    entity = Column(Enum(EntityEnum, name="activity_entity"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    emploee_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    emploee = relationship("Users", foreign_keys=[emploee_id])
    user = relationship("Users", foreign_keys=[user_id])
