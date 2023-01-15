from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from re import compile

from db import get_db
from models import Company
from schemas import GetCompany, CompanySchema
from utils.auth import get_user_by_email, is_superadmin
from utils.api import get_user
from utils.password import secure_pwd

route = APIRouter(prefix="/admin", tags=["Admin"])


@route.post("/company", response_model=GetCompany)
def create_company(company: CompanySchema, api_key: str, db: Session = Depends(get_db)):
    user = get_user(db, api_key, "superadmin")

    if not is_superadmin(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User must be super admin"
        )

    if company.email:
        email_exist, is_company = get_user_by_email(db, company.email)
        if email_exist:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Company with this email already exists",
            )

    name_exist = db.query(Company).filter(Company.name == company.name).first()

    if name_exist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company with this name already exists",
        )

    pattern = compile("[^\s]{8,24}$")
    if not pattern.match(company.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password should between 8 and 24 characters and contain no space",
        )

    company.password = secure_pwd(company.password)

    new_company = Company(**company.dict())

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return new_company
