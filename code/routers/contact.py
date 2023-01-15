from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import get_db
from utils.api import get_user
from models import Contact
from schemas import PostContact, GetContact

route = APIRouter(prefix="/contact", tags=["Contact"])


@route.post("/", response_model=GetContact)
def create(contact: PostContact, api_key: str, db: Session = Depends(get_db)):
    get_user(db, api_key)

    if contact.name == "":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Name is not valid",
        )

    if contact.phone == "":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Phone number is not valid",
        )

    if contact.message == "":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Message is not valid",
        )

    contact = Contact(**contact.dict())

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact


@route.get("/")
def index(api_key: str, db: Session = Depends(get_db)):
    get_user(db, api_key, "superadmin")

    return db.query(Contact).all()
