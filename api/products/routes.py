from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from core.deps import get_db
from api.auth.deps import get_current_user
from api.products import crud
from api.products.schemas import ProductCreate, ProductOut
from api.categories.schemas import CategoryOut, SubCategoryOut
from api.products.schemas import ProductOut as ProductUpdateSchema

from api.activity_logs import crud as activity_crud
from api.activity_logs.schemas import ActivityLogCreate
from core.enums import ActivityLogEnum, EntityEnum
from core.logger import logger

router = APIRouter(
    prefix="/auth",
    tags=["product"],
    dependencies=[Depends(get_current_user)]  # ✅ защита роутера
)

@router.post("/product/add", response_model=dict)
def add_product(
    request: Request,
    db: Session = Depends(get_db),
    product: ProductCreate | None = None
):
    obj = crud.create_product(db, product)
    ip = request.client.host
    actor = request.state.user  

    logger.info(
        f"[PRODUCT][CREATE] actor_id={actor['id']} "
        f"product_id={obj.id} customer_name={product.customer_name} "
        f"count={product.count} category_id={product.category_id} "
        f"sub_category_id={product.sub_category_id} ip={ip}"
    )

    try:
        activity_crud.create_activity_log(
            db,
            ActivityLogCreate(
                action=ActivityLogEnum.create,
                description=(
                    f"Product {obj.id} created by user {actor['id']} "
                    f"({product.customer_name}, count={product.count}) from IP {ip}"
                ),
                entity=EntityEnum.products,
                emploee_id=actor["id"]
            ),
        )
    except Exception:
        logger.exception("Failed to write activity log to DB")

    return {"message": "Product created successfully", "product_id": obj.id}



@router.get("/product/all", response_model=List[ProductOut])
def all_products(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    items = crud.list_products(db, skip, limit)

    logger.info(
        f"[PRODUCT][LIST] user_id={request.state.user['id']} "
        f"skip={skip} limit={limit} count={len(items)} "
        f"ip={request.client.host}"
    )

    out: list[ProductOut] = []
    for p in items:
        out.append(ProductOut(
            id=p.id, customer_name=p.customer_name, count=p.count, length=p.length,
            width=p.width, height=p.height, created_at=p.created_at,
            last_update=p.last_update, status=p.status, total_price=p.total_price,
            description=p.description, category_id=p.category_id,
            sub_category_id=p.sub_category_id,
            category_obj=CategoryOut(
                id=p.category.id,
                name=p.category.name
            ) if p.category else None,
            sub_category_obj=SubCategoryOut(
                id=p.sub_category.id,
                name=p.sub_category.name,
                count=p.sub_category.count,
                category_id=p.sub_category.category_id
            ) if p.sub_category else None
        ))
    return out


@router.put("/product/edit/{product_id}", response_model=dict)
def edit_product(
    request: Request,
    db: Session = Depends(get_db),
    product_id: int = 0,
    product: ProductUpdateSchema | None = None
):
    crud.update_product(db, product_id, product)
    ip = request.client.host
    actor = request.state.user
    changed_fields = list(product.model_dump(exclude_none=True).keys()) if product else []
    
    logger.info(
        f"[PRODUCT][UPDATE] actor_id={actor['id']} "
        f"product_id={product_id} "
        f"fields={changed_fields} "
        f"ip={ip}"
    )

    try:
        activity_crud.create_activity_log(
            db,
            ActivityLogCreate(
                action=ActivityLogEnum.edit,
                description=f"Product {product_id} updated fields {changed_fields} from IP {ip}",
                entity=EntityEnum.products,
                emploee_id=actor["id"]
            ),
        )
    except Exception:
        logger.exception("Failed to write activity log to DB")

    return {"message": "Product updated successfully"}



@router.delete("/product/by-id/{product_id}", response_model=dict)
def delete_product(
    request: Request,
    db: Session = Depends(get_db),
    product_id: int = 0
):
    crud.delete_product(db, product_id)

    logger.info(
        f"[PRODUCT][DELETE] user_id={request.state.user['id']} "
        f"product_id={product_id} ip={request.client.host}"
    )

    return {"detail": "Product deleted successfully"}
