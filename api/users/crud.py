from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.users.models import Users, PersonalDetails
from api.roles.models import Roles

def get_user_by_id(db: Session, user_id: int):
    obj = db.query(Users).filter(Users.id == user_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail='User not found')
    return obj

def list_users_joined(db: Session, skip=0, limit=5):
    return (db.query(Users, PersonalDetails, Roles)
            .join(PersonalDetails, PersonalDetails.user_id == Users.id)
            .join(Roles, Users.role_id == Roles.id)
            .offset(skip).limit(limit).all())

def update_user(db: Session, user_id: int, data):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Connect user with id {user_id} not found")

    user.full_name = f"{data.first_name} {data.last_name}"
    user.email = data.email
    user.description = data.description
    user.role_id = data.role_id

    db.commit()

    det = db.query(PersonalDetails).filter(PersonalDetails.user_id == user_id).first()
    det.phone_number = data.phone
    det.country = data.country
    det.city = data.city
    det.date_of_birth = data.date_of_birth
    db.commit()
