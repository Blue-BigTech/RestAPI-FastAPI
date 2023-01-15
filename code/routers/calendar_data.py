from fastapi import APIRouter, Depends, HTTPException, status
from datetime import date
from sqlalchemy.orm import Session
from typing import List

from utils.api import check_usr_farm
from schemas import GetCalendarData, PostCalendarData
from models import CalendarData
from db import get_db

route = APIRouter(prefix="/calendar-data", tags=["Calendar data"])


@route.get("/{farm_id}", response_model=List[GetCalendarData])
def index(farm_id: str, api_key: str, db: Session = Depends(get_db)):
    check_usr_farm(db, api_key, farm_id)

    calendar_data = db.query(CalendarData).filter(CalendarData.farm == farm_id).all()

    return calendar_data


@route.post("/", response_model=GetCalendarData, status_code=status.HTTP_201_CREATED)
def create(
    calendar_data: PostCalendarData, api_key: str, db: Session = Depends(get_db)
):
    check_usr_farm(db, api_key, calendar_data.farm)

    if calendar_data.title not in [
        "Tilage",
        "Planting",
        "Fertilization",
        "Spraying",
        "Harvesting",
        "Planned Cost",
        "Other",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The title is not valid"
        )

    today = date.today()

    if calendar_data.start_date > today:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The Start Date is not valid"
        )

    if calendar_data.end_date < today:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The End Date is not valid"
        )

    row = CalendarData(**calendar_data.dict())

    db.add(row)
    db.commit()
    db.refresh(row)

    new_calendar_data = db.query(CalendarData).filter(CalendarData.id == row.id).one()

    return new_calendar_data


@route.put("/{id}", response_model=GetCalendarData)
def update(
    id: int,
    calendar_data: PostCalendarData,
    api_key: str,
    db: Session = Depends(get_db),
):
    row = db.query(CalendarData).filter(CalendarData.id == id).first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calendar data not found"
        )

    check_usr_farm(db, api_key, row.farm)

    check_usr_farm(db, api_key, calendar_data.farm)

    today = date.today()

    if calendar_data.start_date > today:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The Start Date is not valid"
        )

    if calendar_data.end_date < today:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The End Date is not valid"
        )

    if calendar_data.title is not None:
        row.title = calendar_data.title

    if calendar_data.description is not None:
        row.description = calendar_data.description

    row.start_date = calendar_data.start_date
    row.end_date = calendar_data.end_date

    db.commit()

    return row


@route.delete("/{id}")
def delete(id: int, api_key: str, db: Session = Depends(get_db)):
    calendar_data = db.query(CalendarData).filter(CalendarData.id == id).one()

    if not calendar_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="There is not calendar data for this id",
        )

    check_usr_farm(db, api_key, calendar_data.farm)

    db.delete(calendar_data)
    db.commit()

    return True
