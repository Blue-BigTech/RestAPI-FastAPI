from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session

from db import get_db
from models import Advisory, Crop
from schemas import PostAdvisorySchema
from utils.api import get_crop, get_user

route = APIRouter(prefix="/advisory", tags=["Advisory"])


@route.get("/all")
def index(api_key: str, db: Session = Depends(get_db)):
    get_user(db, api_key)

    results = db.query(Advisory, Crop).filter(Advisory.crop == Crop.id).all()

    response = list()

    for row in results:
        obj = row[0]
        obj.crop = row[1].name
        response.append(obj)

    return response


@route.post("/create")
def create(
    api_key: str, post_adisory: PostAdvisorySchema, db: Session = Depends(get_db)
):
    get_user(db, api_key)

    selected_crop = get_crop(db, post_adisory.crop)

    new_advisory = Advisory(**post_adisory.dict())
    new_advisory.crop = selected_crop.id

    db.add(new_advisory)
    db.commit()
    db.refresh(new_advisory)

    new_advisory.crop = selected_crop.name
    return new_advisory


@route.get("/")
def show(
    api_key: str,
    crop: str,
    flag: Optional[str] = None,
    stage_growth: Optional[str] = None,
    temp: Optional[float] = None,
    wind: Optional[float] = None,
    rainfall: Optional[float] = None,
    uv: Optional[float] = None,
    soilmoisture: Optional[float] = None,
    db: Session = Depends(get_db),
):

    get_user(db, api_key)

    selected_crop = get_crop(db, crop)

    query = db.query(Advisory)

    if stage_growth:
        query = query.filter(Advisory.stage_growth == stage_growth)

    if flag:
        query = query.filter(Advisory.flag == flag)

    if temp:
        query = query.filter(Advisory.min_temp <= temp, Advisory.max_temp >= temp)

    if wind:
        query = query.filter(Advisory.min_wind <= wind, Advisory.max_wind >= wind)

    if rainfall:
        query = query.filter(
            Advisory.min_rainfall <= rainfall, Advisory.max_rainfall >= rainfall
        )

    if soilmoisture:
        query = query.filter(
            Advisory.min_soilmoisture <= soilmoisture,
            Advisory.max_soilmoisture >= soilmoisture,
        )

    if uv:
        query = query.filter(Advisory.min_uv <= uv, Advisory.max_uv >= uv)

    query = query.all()

    new_list = list()
    for row in query:
        row.crop = selected_crop.name
        new_list.append(row)

    return new_list
