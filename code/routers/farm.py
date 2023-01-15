from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from geoalchemy2 import func
from shapely.wkt import loads
from sqlalchemy import desc
from functools import partial
import shapely.ops as ops
import pyproj
import json

from db import get_db
from models import Farm, FarmCrop, Crop, Scouting, States, CalendarData
from utils.api import (
    get_user,
    get_company,
    check_usr_farm,
    get_crop,
    check_farm_bounds,
    check_crop_params,
)

from schemas import PostFarmCrop, StoreFarmCrop, PostFarm


route = APIRouter(prefix="/farm", tags=["Farm"])


@route.get("/")
def index(api_key: str, db: Session = Depends(get_db)):
    user = None
    company = None

    try:
        user = get_user(db, api_key)
    except Exception:
        pass

    try:
        company = get_company(db, api_key)
    except Exception:
        pass

    if user == None and company == None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Api key does not belong to any user or company",
        )

    if user == None and company == None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Api key does not belong to any user or company",
        )

    if user:
        farms = (
            db.query(func.ST_AsGeoJSON(Farm).label("geom"))
            .filter(Farm.user_id == user.id)
            .all()
        )

    if company:
        farms = (
            db.query(func.ST_AsGeoJSON(Farm).label("geom"))
            .filter(Farm.company_id == company.id)
            .all()
        )

    completeGeoj = {"type": "FeatureCollection", "features": []}

    for farm in farms:
        feat = json.loads(farm["geom"])
        completeGeoj["features"].append(feat)  # type: ignore

    return completeGeoj


@route.post("/register", status_code=status.HTTP_201_CREATED)
def create(farm: PostFarm, api_key: str, db: Session = Depends(get_db)):
    user = None
    company = None

    try:
        user = get_user(db, api_key)
    except Exception:
        pass

    try:
        company = get_company(db, api_key)
    except Exception:
        pass

    if user == None and company == None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Api key does not belong to any user or company",
        )

    if user:
        farm.user_id = user.id
        farm.company_id = user.company_id

    if company:
        if not farm.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Please provide user id"
            )

        if company.id != farm.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User id does not belong to your company",
            )

        farm.company_id = company.id

    if len(farm.name) > 50:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Name cannot be longer than 50 characters",
        )

    if farm.description and len(farm.description) > 200:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Description cannot be longer than 200 characters",
        )

    try:
        polygon = loads(farm.geometry)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The geometry is incorret"
        )

    if polygon.type != "Polygon":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Geometry can only be a polygon",
        )

    # Bounds: -180.0000, -90.0000, 180.0000, 90.0000
    if (
        polygon.bounds[0] < -180
        or polygon.bounds[1] < -90
        or polygon.bounds[2] > 180
        or polygon.bounds[3] > 90
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Something is wrong with the geometry.Check if it's 4326 projection",
        )

    try:
        # source: https://gis.stackexchange.com/questions/127607/calculating-area-in-km%C2%B2-for-polygon-in-wkt-using-python
        # area in hectares
        geom_area = (
            ops.transform(
                partial(
                    pyproj.transform,
                    pyproj.Proj(init="EPSG:4326"),
                    pyproj.Proj(
                        proj="aea", lat_1=polygon.bounds[1], lat_2=polygon.bounds[3]
                    ),
                ),
                polygon,
            ).area
            * 0.0002471054
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Something is wrong with the geometry.Check if it's 4326 projection",
        )

    if geom_area < 0.5:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Area of farm cannot be smaller than 0.5 acre ",
        )

    # will throw error if similar bounds exit
    check_farm_bounds(db, polygon.bounds)
    try:
        (state, country) = (
            db.query(States.name, States.admin)
            .filter(
                func.ST_Within(
                    func.ST_GeomFromText(str(polygon.centroid), 4326), States.geom
                )
            )
            .first()
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not locate farm in any state",
        )

    new_farm = Farm(
        **farm.dict(), bbox=list(polygon.bounds), state=state, country=country
    )

    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)

    my_farm = (
        db.query(func.ST_AsGeoJSON(Farm).label("geom"))
        .filter(Farm.id == new_farm.id)
        .one()
    )

    feat = json.loads(my_farm["geom"])
    completeGeoj = {"type": "FeatureCollection", "features": []}

    completeGeoj["features"].append(feat)  # type: ignore

    return completeGeoj


@route.get("/{id}")
def show(api_key: str, id: str, db: Session = Depends(get_db)):
    farm = check_usr_farm(db, api_key, id)

    completeGeoj = {"type": "FeatureCollection", "features": []}
    farm_feature = json.loads(farm["geom"])

    all_crops = (
        db.query(FarmCrop, Crop.name)
        .filter(FarmCrop.farm_id == farm_feature["properties"]["id"])
        .filter(Crop.id == FarmCrop.crop_id)
        .order_by(desc(FarmCrop.sowing_date))
        .all()
    )

    crops_list = list()
    for crop in all_crops:
        crops_list.append(
            {
                "sowing_date": crop[0].sowing_date,
                "harvesting_date": crop[0].harvesting_date,
                "season": crop[0].season,
                "id": crop[0].id,
                "name": crop[1],
            }
        )

    farm_feature["properties"]["crops"] = crops_list

    completeGeoj["features"].append(farm_feature)  # type: ignore

    return completeGeoj


@route.post("/add-crop")
def create_farm_crop(
    api_key: str, farm_id: str, post_crop: PostFarmCrop, db: Session = Depends(get_db)
):
    selected_farm = check_usr_farm(db, api_key, farm_id)

    crop = get_crop(db, post_crop.crop)

    stored_crop = StoreFarmCrop(
        farm_id=json.loads(selected_farm["geom"])["properties"]["id"],
        crop_id=crop.id,
        **post_crop.dict()
    )

    check_crop_params(
        post_crop.sowing_date, post_crop.harvesting_date, post_crop.season
    )

    stored_crop_dic = stored_crop.dict()
    stored_crop_dic.pop("crop", None)

    stored_crop_dic = FarmCrop(**stored_crop_dic)

    db.add(stored_crop_dic)
    db.commit()
    db.refresh(stored_crop_dic)

    return stored_crop_dic


@route.put("/update-crop", response_model=str)
def update_farm_crop(
    api_key: str,
    farm_id: str,
    crop_id: str,
    post_crop: PostFarmCrop,
    db: Session = Depends(get_db),
):

    selected_farm = check_usr_farm(db, api_key, farm_id)

    selected_farm_id = json.loads(selected_farm["geom"])["properties"]["id"]

    selected_crop = (
        db.query(FarmCrop)
        .filter(FarmCrop.id == crop_id, selected_farm_id == FarmCrop.farm_id)
        .first()
    )

    if not selected_crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Farm crop not found"
        )

    check_crop_params(
        post_crop.sowing_date, post_crop.harvesting_date, post_crop.season
    )

    selected_crop.sowing_date = post_crop.sowing_date
    selected_crop.harvesting_date = post_crop.harvesting_date
    selected_crop.season = post_crop.season

    crop = get_crop(db, post_crop.crop)
    selected_crop.crop_id = crop.id

    db.commit()

    return "success"


@route.delete("/{id}")
def delete(api_key: str, id: str, db: Session = Depends(get_db)):
    check_usr_farm(db, api_key, id)
    
    db.query(FarmCrop).filter(FarmCrop.farm_id == id).delete()
    db.query(Scouting).filter(Scouting.farm == id).delete()
    db.query(CalendarData).filter(CalendarData.farm == id).delete()
    db.query(Farm).filter(Farm.id == id).delete()

    db.commit()

    return True
