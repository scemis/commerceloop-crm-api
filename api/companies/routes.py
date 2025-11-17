from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from core.deps import get_db
from api.auth.deps import get_current_user
from api.companies import crud
from api.companies.schemas import CompanyBase

from api.activity_logs import crud as activity_crud
from api.activity_logs.schemas import ActivityLogCreate
from core.enums import ActivityLogEnum, EntityEnum
from core.logger import logger


router = APIRouter(
    prefix="/auth",
    tags=["company"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/company/add", status_code=201)
def add_company(
    request: Request,
    db: Session = Depends(get_db),
    company: CompanyBase = None
):
    actor = request.state.user
    user_id = actor["id"]
    ip = request.client.host

    obj = crud.create_company(db, company)

    logger.info(
        f"[COMPANY][CREATE] actor_id={user_id} "
        f"company_id={obj.id} name='{company.firm_name}' "
        f"email='{company.email}' phone='{company.phone}' "
        f"ip={ip}"
    )

    try:
        description = (
            f"User {user_id} created company {obj.id} "
            f"('{company.firm_name}', {company.email})."
        )

        activity_crud.create_activity_log(
            db,
            ActivityLogCreate(
                action=ActivityLogEnum.create,
                description=description,
                entity=EntityEnum.companis,
                emploee_id=user_id
            ),
        )
    except Exception:
        logger.exception("Failed to write activity log to DB")

    return {"message": "Company created successfully", "company_id": obj.id}


@router.get("/company/by-name/{name}", response_model=List[CompanyBase])
def by_name(
    request: Request,
    db: Session = Depends(get_db),
    name: Optional[str] = None
):
    items = crud.search_by_name(db, name)

    logger.info(
        f"[COMPANY][GET_BY_NAME] user_id={request.state.user['id']} "
        f"name='{name}' count={len(items)} ip={request.client.host}"
    )

    if not items:
        raise HTTPException(status_code=404, detail="Companies not found")

    return items


@router.get("/company/by-id/{company_id}")
def by_id(
    request: Request,
    company_id: int = 0,
    db: Session = Depends(get_db)
):
    obj = crud.get_company_by_id(db, company_id)

    logger.info(
        f"[COMPANY][GET_BY_ID] user_id={request.state.user['id']} "
        f"company_id={company_id} found={bool(obj)} ip={request.client.host}"
    )

    if not obj:
        raise HTTPException(status_code=404, detail="Company not found")

    return obj


@router.get("/company/all", response_model=List[CompanyBase])
def all_companies(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    items = crud.list_companies(db, skip, limit)

    logger.info(
        f"[COMPANY][LIST] user_id={request.state.user['id']} "
        f"skip={skip} limit={limit} count={len(items)} ip={request.client.host}"
    )

    return items
