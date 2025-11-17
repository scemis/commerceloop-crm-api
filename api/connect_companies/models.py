from sqlalchemy import Column, Integer, Boolean, Text, DateTime, ForeignKey, Enum
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from core.db import Base
from core.enums import StatusEnum

class ConnectCompanis(Base):
    __tablename__ = 'connect_companis'
    id = Column(Integer, primary_key=True, autoincrement=True)
    worker_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    company_id = Column(Integer, ForeignKey('companis.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    next_meeting = Column(DateTime, nullable=True)
    is_approved = Column(Boolean, nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.pending)
    description = Column(Text, nullable=True)
    last_update = Column(DateTime, nullable=True)

    worker = relationship("Users", backref="connect_companis")
    company = relationship("Companis", backref="connect_companis")
