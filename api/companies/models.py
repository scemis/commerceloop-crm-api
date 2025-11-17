from sqlalchemy import Column, Integer, String
from sqlalchemy.types import TIMESTAMP
from datetime import datetime
from core.db import Base

class Companis(Base):
    __tablename__ = 'companis'
    id = Column(Integer, primary_key=True, autoincrement=True)
    firm_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
