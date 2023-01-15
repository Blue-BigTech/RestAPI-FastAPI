from sqlalchemy.orm import Session
from utils.password import secure_pwd

from models import User, Company, Role
from schemas import UserSchema
from fastapi import HTTPException, status


def get_company_by_id(db: Session, id: int):
    company = db.query(Company).filter(Company.id == id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company with company_id does not exist",
        )

    return company


def get_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    company = db.query(Company).filter(Company.id == user_id).first()

    return user or company


def get_user_by_ph(db: Session, ph: int):
    return db.query(User).filter(User.ph == ph).first()


def get_user_by_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    company = db.query(Company).filter(Company.email == email).first()

    is_company = False

    if company:
        is_company = True

    return user or company, is_company


def create_user(db: Session, user: UserSchema):
    user.password = secure_pwd(user.password)

    new_user = User(**user.dict())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Generic function which can check for all roles
def __check_role(user: User, role: Role):
    return user.role == role


# Specific functions which use the generic functions for specific cases
def is_farmer(user: User):
    return __check_role(user, Role.farmer)


def is_agronomist(user: User):
    return __check_role(user, Role.agronomist)


def is_superadmin(user: User):
    return __check_role(user, Role.superadmin)


def is_advisor(user: User):
    return __check_role(user, Role.advisor)
