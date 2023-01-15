from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import get_db
from models import ScheduleCall
from schemas import PostScheduleCall, GetScheduleCall
from utils.api import get_user


route = APIRouter(prefix="/schedule_call", tags=["Schedule Call"])


@route.post("/", response_model=GetScheduleCall, status_code=status.HTTP_201_CREATED)
def create(
    schedule_call: PostScheduleCall, api_key: str, db: Session = Depends(get_db)
):
    get_user(db, api_key)

    if schedule_call.how_to_contact not in [
        "whatsapp",
        "zoom",
        "phone",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The how to contact is not valid",
        )

    if schedule_call.date_time == "":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The datetime is not valid",
        )

    if schedule_call.topic not in [
        "general",
        "disease",
        "plantation",
        "harvesting",
        "pesticides",
        "waste",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The topic is not valid",
        )

    if schedule_call.message == "":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The message is not valid",
        )

    if schedule_call.type_of_expert not in ["local", "international"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The type of expert is not valid",
        )

    schedule_call = ScheduleCall(**schedule_call.dict())

    db.add(schedule_call)
    db.commit()
    db.refresh(schedule_call)

    schedule_call.how_to_contact = schedule_call.how_to_contact.value
    schedule_call.topic = schedule_call.topic.value
    schedule_call.type_of_expert = schedule_call.type_of_expert.value

    return schedule_call


@route.get("/")
def index(api_key: str, db: Session = Depends(get_db)):
    get_user(db, api_key, "superadmin")

    return db.query(ScheduleCall).all()
