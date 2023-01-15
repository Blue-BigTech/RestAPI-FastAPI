from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from shapely.wkt import loads
from typing import List

from utils.api import check_usr_farm
from db import get_db
from schemas import PostScouting, GetScouting
from models import Scouting


route = APIRouter(prefix="/scouting", tags=["Scouting"])


@route.get("/{farm_id}", response_model=List[GetScouting])
def index(farm_id: str, api_key: str, db: Session = Depends(get_db)):
    check_usr_farm(db, api_key, farm_id)

    scoutings = (
        db.query(
            Scouting.farm,
            Scouting.geometry.ST_AsGeoJSON().label("geometry"),
            Scouting.note_type,
            Scouting.id,
            Scouting.comments,
            Scouting.attachment,
        )
        .filter(Scouting.farm == farm_id)
        .all()
    )

    return scoutings


@route.post("/", response_model=GetScouting, status_code=status.HTTP_201_CREATED)
def create(scouting: PostScouting, api_key: str, db: Session = Depends(get_db)):
    check_usr_farm(db, api_key, scouting.farm)

    try:
        loads(scouting.geometry)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The geometry is incorrect"
        )

    if scouting.note_type not in [
        "Disease",
        "Pests",
        "Water logging",
        "Weeds",
        "Lodging",
        "Others",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The note type is not valid"
        )

    scouting = Scouting(**scouting.dict())

    db.add(scouting)
    db.commit()
    db.refresh(scouting)

    (scouting.geometry,) = (
        db.query(Scouting.geometry.ST_AsGeoJSON())
        .filter(Scouting.id == scouting.id)
        .one()
    )

    return scouting


@route.put("/{id}", response_model=GetScouting)
def update(
    id: int, scouting: PostScouting, api_key: str, db: Session = Depends(get_db)
):
    check_usr_farm(db, api_key, scouting.farm)

    row = db.query(Scouting).filter(Scouting.id == id).first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scouting not found"
        )

    try:
        loads(scouting.geometry)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The geometry is incorrect"
        )

    if scouting.note_type not in [
        "Disease",
        "Pests",
        "Water logging",
        "Weeds",
        "Lodging",
        "Others",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The note type is not valid"
        )

    if scouting.comments is not None:
        row.comments = scouting.comments

    if scouting.attachment is not None:
        row.attachment = scouting.attachment

    row.geometry = scouting.geometry
    row.note_type = scouting.note_type

    db.commit()

    updated_row = (
        db.query(
            Scouting.farm,
            Scouting.geometry.ST_AsGeoJSON().label("geometry"),
            Scouting.note_type,
            Scouting.id,
            Scouting.comments,
            Scouting.attachment,
        )
        .filter(Scouting.id == id)
        .first()
    )

    return updated_row
