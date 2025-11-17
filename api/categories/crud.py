from fastapi import HTTPException
from sqlalchemy.orm import Session
from api.categories import models
from api.categories.schemas import SubCategoryUpdate

def create_category(db: Session, name: str):
    if db.query(models.Category).filter(models.Category.name == name).first():
        raise HTTPException(status_code=400, detail='Category already exists')
    obj = models.Category(name=name)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def list_categories(db: Session, skip=0, limit=100):
    return (db.query(models.Category)
              .order_by(models.Category.id.desc())
              .offset(skip).limit(limit).all())

def delete_category(db: Session, category_id: int):
    if db.query(models.SubCategory).filter(models.SubCategory.category_id == category_id).first():
        raise HTTPException(status_code=404, detail='Category cannot be deleted because it has subcategories')
    obj = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not obj: raise HTTPException(status_code=404, detail='No category found with the given ID')
    db.delete(obj); db.commit()

def update_category(db: Session, category_id: int, name: str):
    obj = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not obj: raise HTTPException(status_code=404, detail='Category not found')
    if db.query(models.Category).filter(models.Category.name == name).first():
        raise HTTPException(status_code=400, detail='Category name already exists')
    obj.name = name; db.commit(); db.refresh(obj)
    return obj

def create_subcategory(db: Session, data):
    if not db.query(models.Category).filter(models.Category.id == data.category_id).first():
        raise HTTPException(status_code=400, detail='Category does not exist')
    if db.query(models.SubCategory).filter(models.SubCategory.name == data.name).first():
        raise HTTPException(status_code=400, detail='Subcategory already exists')
    obj = models.SubCategory(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def list_subcategories(db: Session, skip=0, limit=100):
    return (db.query(models.SubCategory)
              .order_by(models.SubCategory.id.desc())
              .offset(skip).limit(limit).all())

def list_subcategories_by_category(db: Session, category_id: int):
    return (db.query(models.SubCategory)
              .filter(models.SubCategory.category_id == category_id)
              .order_by(models.SubCategory.id.desc()).all())

def update_subcategory(db: Session, subcategory_id: int, data: SubCategoryUpdate):
    obj = db.query(models.SubCategory).filter(models.SubCategory.id == subcategory_id).first()
    if not obj: raise HTTPException(status_code=404, detail="Subcategory not found")
    obj.name = data.name
    obj.count = data.count
    obj.booked = obj.booked if data.booked == -1 else data.booked
    obj.height, obj.width, obj.length = data.height, data.width, data.length
    obj.price_per_piece = data.price_per_piece
    db.commit(); db.refresh(obj)
    return obj

def delete_subcategory(db: Session, subcategory_id: int):
    obj = db.query(models.SubCategory).filter(models.SubCategory.id == subcategory_id).first()
    if not obj: raise HTTPException(status_code=404, detail='No subcategory found with the given ID')
    db.delete(obj); db.commit()
