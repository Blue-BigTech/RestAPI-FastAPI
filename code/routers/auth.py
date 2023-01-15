from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from re import compile

from schemas import UserSchema, Token, uuidofuser
from db import get_db
from utils.password import verify_pwd
from utils.outh2 import create_access_token
from utils.auth import get_user_by_ph, create_user, get_user_by_email, get_company_by_id

route = APIRouter(prefix="/auth", tags=["Authentication"])


@route.post("/register", response_model=uuidofuser)
def register(user: UserSchema, db: Session = Depends(get_db)):

    get_company_by_id(db, user.company_id)

    available = get_user_by_ph(db, user.ph)

    if available:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with same phone number exists",
        )

    if user.email:
        email_exists, is_company = get_user_by_email(db, user.email)
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User with this email already exists",
            )

    # matches everything except `empty space` with min 8 and max 24 characters.
    pattern = compile("[^\s]{8,24}$")
    if not pattern.match(user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password should between 8 and 24 characters and contain no space",
        )

    new_user = create_user(db, user)

    return new_user


@route.post("/login", response_model=Token)
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    current_user = None

    # if logging in via phone number
    try:
        phone = int(user.username)
        current_user = get_user_by_ph(db, phone)
        is_company = False
    except Exception:
        current_user, is_company = get_user_by_email(db, user.username)

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with the phone/email does not exist",
        )

    if not (verify_pwd(user.password, current_user.password)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Password incorrect"
        )

    if is_company:
        company_id = current_user.id
    else:
        company_id = current_user.company_id

    token = create_access_token({"user_id": current_user.id, "company_id": company_id})

    return Token(access_token=token, api_key=current_user.apikey)
