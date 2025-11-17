from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from api.products.models import Product
from api.categories.models import SubCategory, Category

def create_product(db: Session, data):
    obj = Product(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)

    sub = db.query(SubCategory).filter(SubCategory.id == data.sub_category_id).first()
    sub.booked += data.count
    db.commit()
    return obj

def list_products(db: Session, skip=0, limit=100):
    return (db.query(Product)
            .options(joinedload(Product.category), joinedload(Product.sub_category))
            .order_by(Product.id.desc()).offset(skip).limit(limit).all())

def update_product(db: Session, product_id: int, data):
    obj = db.query(Product).filter(Product.id == product_id).first()
    if not obj: raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
    if data.status.value == 'canceled':
        data.count = 0

    sub = db.query(SubCategory).filter(SubCategory.id == obj.sub_category_id).first()
    sub.booked -= obj.count - data.count

    for field, value in data.model_dump().items():
        setattr(obj, field, value)
    obj.last_update = datetime.utcnow()
    db.commit()
    return obj

def delete_product(db: Session, product_id: int):
    obj = db.query(Product).filter(Product.id == product_id).first()
    if not obj: raise HTTPException(status_code=404, detail='No product found with the given ID')
    sub = db.query(SubCategory).filter(SubCategory.id == obj.sub_category_id).first()
    sub.booked -= obj.count
    db.delete(obj); db.commit()
