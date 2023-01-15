from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db import get_db
from models import Disease
from schemas import DiseaseSchema, GetDisease


route = APIRouter(prefix="/disease", tags=["Crop Diseases"])


@route.get("/all", response_model=List[GetDisease])
def index(db: Session = Depends(get_db)):
    return db.query(Disease).all()


@route.post("/register", status_code=status.HTTP_201_CREATED, response_model=GetDisease)
def create(disease: DiseaseSchema, db: Session = Depends(get_db)):
    new_disease = Disease(**disease.dict())

    db.add(new_disease)
    db.commit()
    db.refresh(new_disease)

    return new_disease


@route.get("/{id}", response_model=GetDisease)
def show(id: str, db: Session = Depends(get_db)):
    disease = db.query(Disease).filter(Disease.id == id).one()

    if not disease:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease with given ID does not exist",
        )

    return disease
