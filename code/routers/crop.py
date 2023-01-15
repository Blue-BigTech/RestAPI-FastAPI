from fastapi import APIRouter, Depends, HTTPException, status
from schemas import PostCrop, GetCrop, CropStageSchema
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from db import get_db
from models import Crop, CropStage, FarmCrop
from utils.api import check_usr_farm, get_user

route = APIRouter(prefix="/crop", tags=["Crop"])


@route.get("/", response_model=List[GetCrop])
def index(db: Session = Depends(get_db)):
    return db.query(Crop).all()


@route.post("/", response_model=GetCrop, status_code=status.HTTP_201_CREATED)
def create(crop: PostCrop, db: Session = Depends(get_db)):

    duplicate = db.query(Crop).filter(Crop.name == crop.name).first()

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Crop with the name already exists",
        )

    new_crop = Crop(**crop.dict())

    db.add(new_crop)
    db.commit()
    db.refresh(new_crop)

    return new_crop


@route.get("/crop_stage", response_model=List[CropStageSchema])
def get_crop_stage(api_key: str, farm_id: str, db: Session = Depends(get_db)):
    check_usr_farm(db, api_key, farm_id)

    latest_crop = (
        db.query(FarmCrop.crop_id)
        .filter(FarmCrop.farm_id == farm_id)
        .order_by(desc(FarmCrop.sowing_date))
        .first()
    )

    if not latest_crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Crops found to return crop stage information. Please add crops.",
        )

    crop_stages = (
        db.query(CropStage).filter(CropStage.crop == latest_crop.crop_id).all()
    )

    return crop_stages


@route.get("/{name}", response_model=GetCrop)
def show(name: str, api_key: str, db: Session = Depends(get_db)):

    get_user(db, api_key)

    result = db.query(Crop).filter(Crop.name == name).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found"
        )

    return result
