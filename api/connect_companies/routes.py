from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from core.deps import get_db
from api.auth.deps import get_current_user   # ✅ общий депенденси (ставим на роутер)
from api.connect_companies import crud
from api.connect_companies.schemas import (
    CreateConnectCompanyRequest,
    EditConnectCompanyRequest,
    ConnectCompanyOut,
)

from api.activity_logs import crud as activity_crud
from api.activity_logs.schemas import ActivityLogCreate
from core.enums import ActivityLogEnum, EntityEnum
from core.logger import logger

router = APIRouter(
    prefix="/auth",
    tags=["recallCompany"],
    dependencies=[Depends(get_current_user)]  # ✅ защита на уровне роутера
)

@router.post("/recallCompanis/add", status_code=201)
def create_connect_company(
    request: Request,
    db: Session = Depends(get_db),
    connectCompany: CreateConnectCompanyRequest | None = None,
):
    actor_id = request.state.user["id"]
    ip = request.client.host
    obj = crud.create_with_company(db, actor_id, connectCompany)

    logger.info(
        f"[RECALL_COMPANY][CREATE] actor_id={actor_id} "
        f"company_id={getattr(obj, 'company_id', None)} "
        f"connect_id={getattr(obj, 'id', None)} "
        f"next_meeting={getattr(obj, 'next_meeting', None)} "
        f"is_approved={getattr(obj, 'is_approved', None)} "
        f"status={getattr(obj, 'status', None)} "
        f"ip={ip}"
    )

    try:
        activity_crud.create_activity_log(
            db,
            ActivityLogCreate(
                action=ActivityLogEnum.create,
                description=(
                    f"Recall company entry created: connect_id={getattr(obj, 'id', None)}, "
                    f"company_id={getattr(obj, 'company_id', None)}, "
                    f"status={getattr(obj, 'status', None)}, next_meeting={getattr(obj, 'next_meeting', None)}, "
                    f"ip={ip}"
                ),
                entity=EntityEnum.connect_companis,
                emploee_id=actor_id
            ),
        )
    except Exception:
        logger.exception("Failed to write activity log to DB")

    return {
        "message": "Company and connection created successfully.",
        "id": getattr(obj, "id", None),
    }


@router.get("/recallCompanis/by-pt-id/{connectCompany_id}")
def read_connect_company(
    request: Request,
    connectCompany_id: int = 0,
    db: Session = Depends(get_db),
):
    obj = crud.get_by_id(db, connectCompany_id)

    logger.info(
        f"[RECALL_COMPANY][GET_BY_ID] user_id={request.state.user['id']} "
        f"connect_id={connectCompany_id} found={bool(obj)} "
        f"ip={request.client.host}"
    )

    if not obj:
        raise HTTPException(status_code=404, detail="Connect company not found")
    return obj

@router.get("/recallCompanis/by-worker-id/{worker_id}", response_model=List[ConnectCompanyOut])
def by_worker(
    request: Request,
    db: Session = Depends(get_db),
    worker_id: int = 0,
):
    items = crud.list_by_worker(db, worker_id)

    logger.info(
        f"[RECALL_COMPANY][BY_WORKER] user_id={request.state.user['id']} "
        f"worker_id={worker_id} count={len(items)} ip={request.client.host}"
    )

    return items

@router.get("/potentialCompanies/all", response_model=List[CreateConnectCompanyRequest])
def potential(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 5,
):
    rows = crud.list_potential(db, skip, limit)

    logger.info(
        f"[RECALL_COMPANY][POTENTIAL_LIST] user_id={request.state.user['id']} "
        f"skip={skip} limit={limit} count={len(rows)} ip={request.client.host}"
    )

    return [
        CreateConnectCompanyRequest(
            company_id=r.company.id,
            firm_name=r.company.firm_name,
            email=r.company.email,
            phone=r.company.phone,
            next_meeting=r.next_meeting,
            is_approved=r.is_approved,
            status=r.status,
            description=r.description,
            last_update=r.last_update,
        )
        for r in rows
    ]

@router.put("/recallCompanis/edit/{connect_company_id}")
def edit_connect_company(
    request: Request,
    db: Session = Depends(get_db),
    connect_company_id: int = 0,
    connectCompany: EditConnectCompanyRequest | None = None,
):
    actor = request.state.user
    user_id = actor["id"]
    ip = request.client.host
    crud.update_connect(db, connect_company_id, connectCompany)

    logger.info(
        f"[RECALL_COMPANY][UPDATE] actor_id={user_id} "
        f"connect_company_id={connect_company_id} "
        f"is_approved={getattr(connectCompany, 'is_approved', None)} "
        f"status={getattr(connectCompany, 'status', None)} "
        f"next_meeting={getattr(connectCompany, 'next_meeting', None)} "
        f"ip={ip}"
    )

    try:
        changed_fields = list(connectCompany.model_dump(exclude_none=True).keys()) \
            if connectCompany else []

        description = (
            f"User {user_id} updated connection company {connect_company_id}. "
            f"Changed fields: {changed_fields}"
        )

        activity_crud.create_activity_log(
            db,
            ActivityLogCreate(
                action=ActivityLogEnum.edit,
                description=description,
                entity=EntityEnum.connect_companis,
                emploee_id=user_id
            ),
        )
    except Exception:
        logger.exception("Failed to write activity log to DB")

    return {"message": "Connect company updated successfully"}

