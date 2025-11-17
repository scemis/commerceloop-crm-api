# api/categories/routes.py
from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from core.deps import get_db
from api.auth.deps import get_current_user
from api.categories import crud
from api.categories.schemas import (
    CategoryCreate, CategoryOut,
    SubCategoryCreate, SubCategoryUpdate, SubCategoryOut
)

# logging
from core.logger import logger
from api.activity_logs import crud as activity_crud
from api.activity_logs.schemas import ActivityLogCreate
from core.enums import ActivityLogEnum, EntityEnum


router = APIRouter(
    prefix="/auth",
    tags=["category"],
    dependencies=[Depends(get_current_user)]
)


# -----------------------------
# CATEGORY
# -----------------------------

@router.post("/category/add", response_model=dict)
def create_category(
    request: Request,
    db: Session = Depends(get_db),
    category: CategoryCreate | None = None
):
    obj = crud.create_category(db, category.name)

    ip = request.client.host
    logger.info(f"Category created | id={obj.id} name={obj.name} ip={ip}")

    try:
        activity_crud.create_activity_log(
            db,
            ActivityLogCreate(
                action=ActivityLogEnum.create,
                description=f"Created category '{obj.name}' from {ip}",
                entity=EntityEnum.categories,
                emploee_id=request.state.user.id
            ),
        )
    except Exception:
        logger.exception("Failed to write category creation log to DB")

    return {"message": "Category created successfully", "category_id": obj.id}


@router.get("/category/all", response_model=List[CategoryOut])
def list_categories(request: Request, db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    logger.info(f"Category list requested from {request.client.host}")
    return crud.list_categories(db, skip, limit)


@router.delete("/category/by-id/{category_id}")
def delete_category(category_id: int, request: Request, db: Session = Depends(get_db)):
    crud.delete_category(db, category_id)

    ip = request.client.host
    logger.info(f"Category deleted | id={category_id} ip={ip}")

    try:
        activity_crud.create_activity_log(
            db,
            ActivityLogCreate(
                action=ActivityLogEnum.delete,
                description=f"Deleted category id={category_id} from {ip}",
                entity=EntityEnum.categories,
                emploee_id=request.state.user.id
            ),
        )
    except Exception:
        logger.exception("Failed to write delete category log to DB")

    return {"detail": "Category deleted successfully"}


@router.put("/category/{category_id}", response_model=dict)
def update_category(
    category_id: int,
    category: CategoryCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    obj = crud.update_category(db, category_id, category.name)

    ip = request.client.host
    logger.info(f"Category updated | id={obj.id} name={obj.name} ip={ip}")

    try:
        activity_crud.create_activity_log(
            db,
            ActivityLogCreate(
                action=ActivityLogEnum.edit,
                description=f"Updated category '{obj.name}' from {ip}",
                entity=EntityEnum.categories,
                emploee_id=request.state.user.id
            ),
        )
    except Exception:
        logger.exception("Failed to write update category log to DB")

    return {"message": "Category updated successfully", "category_id": obj.id}


# -----------------------------
# SUBCATEGORY
# -----------------------------

@router.post("/subcategory/add", response_model=dict)
def create_subcategory(
    sub_category: SubCategoryCreate | None = None,
    request: Request = None,
    db: Session = Depends(get_db),
):
    obj = crud.create_subcategory(db, sub_category)

    ip = request.client.host
    logger.info(f"Subcategory created | id={obj.id} name={obj.name} ip={ip}")

    try:
        activity_crud.create_activity_log(
            db,
            ActivityLogCreate(
                action=ActivityLogEnum.create,
                description=f"Created subcategory '{obj.name}' from {ip}",
                entity=EntityEnum.sub_categories,
                emploee_id=request.state.user.id
            ),
        )
    except Exception:
        logger.exception("Failed to write subcategory creation log to DB")

    return {"message": "Subcategory created successfully", "subcategory_id": obj.id}


@router.get("/subcategory/all", response_model=List[SubCategoryOut])
def list_subcategories(request: Request, db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    logger.info(f"Subcategory list requested from {request.client.host}")
    subs = crud.list_subcategories(db, skip, limit)

    return [
        SubCategoryOut(
            id=s.id, name=s.name, count=s.count, booked=s.booked or 0,
            length=s.length, width=s.width, height=s.height,
            price_per_piece=s.price_per_piece, category_id=s.category_id,
            balance=(s.count or 0) - (s.booked or 0),
            m3=round(((s.length * s.width * s.height) / 1_000_000_000) *
                     ((s.count or 0) - (s.booked or 0)), 2)
        ) for s in subs
    ]


@router.get("/subcategories/by-category-id/{category_id}", response_model=List[SubCategoryOut])
def list_by_category(category_id: int, request: Request, db: Session = Depends(get_db)):
    logger.info(f"Subcategory list by category requested | category_id={category_id} ip={request.client.host}")
    subs = crud.list_subcategories_by_category(db, category_id)

    return [
        SubCategoryOut(
            id=s.id, name=s.name, count=s.count, booked=s.booked or 0,
            length=s.length, width=s.width, height=s.height,
            price_per_piece=s.price_per_piece, category_id=s.category_id,
            balance=(s.count or 0) - (s.booked or 0),
            m3=round((s.length * s.width * s.height) / 1_000_000_000 *
                     ((s.count or 0) - (s.booked or 0)), 5)
        ) for s in subs
    ]


@router.delete("/subcategory/by-id/{subcategory_id}")
def delete_subcategory(subcategory_id: int, request: Request, db: Session = Depends(get_db)):
    crud.delete_subcategory(db, subcategory_id)

    ip = request.client.host
    logger.info(f"Subcategory deleted | id={subcategory_id} ip={ip}")

    try:
        activity_crud.create_activity_log(
            db,
            ActivityLogCreate(
                action=ActivityLogEnum.delete,
                description=f"Deleted subcategory id={subcategory_id} from {ip}",
                entity=EntityEnum.sub_categories,
                emploee_id=request.state.user.id
            ),
        )
    except Exception:
        logger.exception("Failed to write delete subcategory log to DB")

    return {"detail": "Sub category deleted successfully"}


@router.put("/subcategory/{subcategory_id}", response_model=dict)
def update_subcategory(
    subcategory_id: int,
    sub_category: SubCategoryUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    obj = crud.update_subcategory(db, subcategory_id, sub_category)

    ip = request.client.host
    logger.info(f"Subcategory updated | id={obj.id} name={obj.name} ip={ip}")

    try:
        activity_crud.create_activity_log(
            db,
            ActivityLogCreate(
                action=ActivityLogEnum.edit,
                description=f"Updated subcategory '{obj.name}' from {ip}",
                entity=EntityEnum.sub_categories,
                emploee_id=request.state.user.id,
                user_id=request.state.user.id,
            ),
        )
    except Exception:
        logger.exception("Failed to write update subcategory log to DB")

    return {"message": "Subcategory updated successfully", "subcategory_id": obj.id}
