from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Text
from sqlalchemy.types import TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from core.db import Base
from core.enums import StatusEnum

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(255), nullable=False)
    count = Column(Integer, nullable=False, default=0)
    length = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_update = Column(DateTime, nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.pending)
    total_price = Column(Float, nullable=False, default=0)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"))
    sub_category_id = Column(Integer, ForeignKey("sub_categories.id", ondelete="CASCADE"))
    category = relationship("Category", backref="products")
    sub_category = relationship("SubCategory", backref="products")
