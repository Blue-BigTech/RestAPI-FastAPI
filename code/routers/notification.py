from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from shapely.wkt import loads

from models import Farm, User
from schemas import Notification
from db import get_db
from utils.api import get_user

route = APIRouter(prefix="/notification", tags=["Notification"])


@route.post("/", status_code=status.HTTP_200_OK)
def send_notification(
    notification: Notification, api_key: str, db: Session = Depends(get_db)
):
    get_user(db, api_key)

    if not notification.title or notification.title == "":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The title is not valid"
        )

    if not notification.description or notification.description == "":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The description is not valid"
        )

    if not notification.date_time or notification.date_time == "":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The datetime is not valid"
        )

    try:
        loads(notification.polygon)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The polygon is incorrect"
        )

    farms = (
        db.query(Farm.id.label("farm_id"), Farm.user_id, User.email, User.ph)
        .filter(Farm.geometry.ST_Intersects(notification.polygon))
        .join(User)
        .filter(Farm.user_id == User.id)
        .all()
    )

    return farms
