from sqlalchemy import Column, Integer, String, Text, Date, Boolean, ForeignKey
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from core.db import Base

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    last_date_connection = Column(Date, nullable=True)
    is_deleted = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE', onupdate='CASCADE'))
    hashed_pass = Column(Text, nullable=False)
    role = relationship("Roles", backref="users")

class PersonalDetails(Base):
    __tablename__ = 'personal_details'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    phone_number = Column(String(15), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("Users", backref="personal_details")
