from sqlalchemy import Column, Integer, String
from core.db import Base

class Roles(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), unique=True, nullable=False)
