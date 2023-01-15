from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from geoalchemy2 import func
from typing import List, Literal
from sqlalchemy import String
from datetime import datetime
import json

from models import User, Company, Farm, Crop, Indice


def get_user(db: Session, api: str, role: str = "farmer"):
    user = db.query(User).filter(User.apikey == api, User.role == role).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with given key and role does not exist",
        )

    return user


def get_company(db: Session, api: str):
    user = db.query(Company).filter(Company.apikey == api).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company with given key does not exist",
        )

    return user


def check_farm_bounds(db: Session, bounds: List[int]):
    check_farm = (
        db.query(Farm).filter(Farm.bbox.cast(String) == json.dumps(bounds)).first()
    )

    if check_farm:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Farm with the given bounds already exists",
        )

    return None


def check_usr_farm(db: Session, api: str, id: str):
    user = get_user(db, api)

    farm = (
        db.query(func.ST_AsGeoJSON(Farm).label("geom"))
        .filter(Farm.user_id == user.id, Farm.id == id)
        .first()
    )

    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm with given id not found for API key",
        )

    return farm


def get_crop(db: Session, crop_name: str):
    crop = db.query(Crop).filter(Crop.name == crop_name).first()

    if not crop:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Crop with the given name does not exist",
        )

    return crop


def check_crop_params(sowing_date, harvesting_date, season):
    if sowing_date > datetime.today().date():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sowing date cannot be greater than today",
        )

    # harvesting date is optional
    if harvesting_date and harvesting_date <= sowing_date:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Harvesting date cannot be greater or equal to sowing date",
        )

    if season < 2015 or season > (datetime.today().year + 1):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Season should be between 2015 and {datetime.today().year}",
        )

    return None


def check_indice(db: Session, name: str, type: Literal["imagery", "statistics"]):

    columns = {"imagery": "evalscript", "statistics": "statistical_evalscript"}

    selected_indice = (
        db.query(Indice)
        .filter(Indice.name == name)
        .filter(getattr(Indice, columns[type]).isnot(None))
        .first()
    )

    if not selected_indice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Index not found for ${type}",
        )

    return selected_indice
