from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.types import TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from core.db import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

class SubCategory(Base):
    __tablename__ = "sub_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    count = Column(Integer, nullable=False, default=0)
    booked = Column(Integer, nullable=False, default=0)
    length = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    price_per_piece = Column(Float, nullable=False, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", backref="sub_categories")
