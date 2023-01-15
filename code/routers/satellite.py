from sentinelhub import (
    SentinelHubRequest,
    SentinelHubCatalog,
    DataCollection,
    SentinelHubStatistical,
    MimeType,
    CRS,
    BBox,
    SHConfig,
    Geometry,
)
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from typing import List
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import case
from geoalchemy2 import func
from PIL import Image
import numpy as np
import io, os
from imageio import v3 as iio
import rasterio as rio
from pathlib import Path
from starlette.background import BackgroundTasks
from rasterio import mask as msk
from dateutil import parser
from concurrent.futures import ThreadPoolExecutor
import shutil
import json

from config import setting
from db import get_db
from models import Farm, satellite, User, Indice
from schemas import getIndexValue, getIndice
from utils.api import check_usr_farm, check_indice
from uuid import uuid4


def read_file(file):
    with rio.open(file) as src:
        return src.read()


route = APIRouter(prefix="/satellite", tags=["Satellite"])

SENTINEL_HUB_CLIENT_ID = setting.SENTINEL_HUB_CLIENT_ID
SENTINEL_HUB_CLIENT_SECRET = setting.SENTINEL_HUB_CLIENT_SECRET


def remove_file(path: str) -> None:
    os.unlink(path)


def remove_folder(path: str) -> None:
    shutil.rmtree(path)


@route.get("/dates/{id}")
async def get_satellites(id: str, api_key: str, db: Session = Depends(get_db)):
    getFarm = check_usr_farm(db, api_key, id)
    # This is script may only work with sentinelhub.__version__ >= '3.4.0'
    # Credentials
    farm_geom = json.loads(getFarm["geom"])

    bbox = BBox(bbox=farm_geom["properties"]["bbox"], crs=CRS.WGS84)
    today = datetime.now()
    yesterday = today - timedelta(days=365)

    satellites = db.query(satellite).filter(satellite.catalogue == True).all()

    catalogs = []
    for product in satellites:
        config = SHConfig()
        config.sh_client_id = SENTINEL_HUB_CLIENT_ID
        config.sh_client_secret = SENTINEL_HUB_CLIENT_SECRET
        config.sh_base_url = product.region_url

        catalog = SentinelHubCatalog(config=config)

        catalogs.append(
            catalog.search(collection=product.name, bbox=bbox, time=(yesterday, today))
        )

    executions = []
    with ThreadPoolExecutor() as executor:
        executions = [executor.submit(list, catalog) for catalog in catalogs]  # type: ignore

    results = [execution.result() for execution in executions]

    core_result = []
    for products in results:
        for result in products:
            collection = result["collection"]  # type: ignore
            satellite_name = next(
                x.satellite for x in satellites if x.name == collection
            )
            oneobj = {
                "satellite": satellite_name,
                # TODO: Not available in one satellite
                # "constellation": result['properties']['constellation'],
                # "platform" : result['properties']['platform'],
                "datetime": result["properties"]["datetime"],  # type: ignore
                "cloud_cover": None,
            }

            if "eo:cloud_cover" in result["properties"]:  # type: ignore
                oneobj["cloud_cover"] = result["properties"]["eo:cloud_cover"]  # type: ignore
            core_result.append(oneobj)

    core_result = sorted(
        core_result, key=lambda x: parser.parse(x["datetime"]), reverse=True
    )
    return core_result


@route.get("/field-imagery", response_class=Response)
async def get_field_imagey(
    farm_id: str,
    index: str,
    api_key: str,
    satellite_date: date,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):

    selected_indice = check_indice(db, index, "imagery")

    getFarm = check_usr_farm(db, api_key, farm_id)
    farm_geom = json.loads(getFarm["geom"])

    curr_satellite = (
        db.query(satellite).filter(satellite.name == selected_indice.satellite).one()
    )

    config = SHConfig()
    config.sh_client_id = SENTINEL_HUB_CLIENT_ID
    config.sh_client_secret = SENTINEL_HUB_CLIENT_SECRET
    config.sh_base_url = curr_satellite.region_url

    collection = next(
        x for x in list(DataCollection) if x.api_id == selected_indice.satellite
    )

    bbox = BBox(bbox=farm_geom["properties"]["bbox"], crs=CRS.WGS84)
    geometry = Geometry(geometry=farm_geom["geometry"], crs=CRS.WGS84)

    today = satellite_date
    yesterday = today - timedelta(days=500)
    data_folder = f"static/field-imagery-{uuid4()}"
    try:
        request = SentinelHubRequest(
            data_folder=data_folder,
            evalscript=selected_indice.evalscript,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=collection,
                    time_interval=(yesterday, today),
                ),
            ],
            responses=[
                SentinelHubRequest.output_response("default", MimeType.TIFF),
            ],
            bbox=bbox,
            config=config,
        )
        response = request.get_data(save_data=True)

        full_path = f"{data_folder}/{next(os.walk(data_folder))[1][0]}"

        with rio.open(f"{full_path}/response.tiff") as src:  # type: ignore
            out_image, out_transform = msk.mask(
                src, [farm_geom["geometry"]], crop=True, nodata=0
            )
            out_meta = src.meta.copy()
            out_meta.update(
                {
                    "driver": "PNG",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform,
                    "nodata": 0,
                }
            )

        with rio.open(f"{full_path}/masked.png", "w", **out_meta) as dst:
            dst.write(out_image)
            dst.close()

        background_tasks.add_task(remove_folder, data_folder)
        return FileResponse(f"{full_path}/masked.png")
    except Exception as e:
        print(e)
        remove_folder(data_folder)


@route.post("/indextiff")  # ,response_class=Response)
def get_index(
    postdata: getIndexValue,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):

    getFarm = (
        db.query(func.ST_AsGeoJSON(Farm).label("geom"))
        .filter(Farm.id == postdata.farm_id)
        .one()
    )

    farm_geom = json.loads(getFarm["geom"])
    # This is script may only work with sentinelhub.__version__ >= '3.4.0'

    # Credentials
    selected_indice = db.query(Indice).filter(Indice.name == postdata.index).one()

    if not selected_indice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Index not found in the table",
        )

    curr_satellite = (
        db.query(satellite).filter(satellite.name == selected_indice.satellite).one()
    )

    config = SHConfig()
    config.sh_client_id = SENTINEL_HUB_CLIENT_ID
    config.sh_client_secret = SENTINEL_HUB_CLIENT_SECRET
    config.sh_base_url = curr_satellite.region_url

    collection = next(
        x for x in list(DataCollection) if x.api_id == selected_indice.satellite
    )

    bbox = BBox(bbox=farm_geom["properties"]["bbox"], crs=CRS.WGS84)
    geometry = Geometry(geometry=farm_geom["geometry"], crs=CRS.WGS84)

    today = postdata.satellite_date
    yesterday = today - timedelta(days=500)
    currentTime = f"{str(datetime.now())}"

    request = SentinelHubRequest(
        data_folder=currentTime,
        evalscript=selected_indice.evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=collection,
                time_interval=(yesterday, today),
            ),
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.TIFF),
        ],
        bbox=bbox,
        geometry=geometry,
        config=config,
    )
    ############ GET TIFF

    all_bands_img = request.get_data(save_data=True)
    tmp_file = Path(f"static/{currentTime}.tiff")

    for folder, _, filenames in os.walk(request.data_folder):  # type: ignore
        for filename in filenames:
            if filename == "response.tiff":
                with rio.open(os.path.join(folder, filename)) as src:  # type: ignore
                    out_image, out_transform = msk.mask(
                        src, [farm_geom["geometry"]], crop=True
                    )
                    out_meta = src.meta.copy()
                    out_meta.update(
                        {
                            "driver": "GTiff",
                            "height": out_image.shape[1],
                            "width": out_image.shape[2],
                            "transform": out_transform,
                        }
                    )
                # b4 = rio.open(os.path.join(folder, filename))
                # data_array= b4.read()
                # metandvi = b4.meta
                # metandvi.update(driver='GTiff')
                with rio.open(tmp_file, "w", **out_meta) as dst:
                    dst.write(out_image)
                    dst.close()
                array_list = read_file(tmp_file)
                for i, array in enumerate(array_list):
                    nparray = np.array(array)
                    nparray = nparray.astype(np.uint8)
                    im = Image.fromarray(nparray)

                    with io.BytesIO() as buf:
                        iio.imwrite(buf, im, plugin="pillow", format="png")
                        im_bytes = buf.getvalue()

                    return Response(im_bytes, media_type="image/png")
                # Return the data in the 'temporary' file
                background_tasks.add_task(remove_file, tmp_file)  # type: ignore
                background_tasks.add_task(remove_folder, currentTime + "/")

                return FileResponse(tmp_file)


@route.get("/indices", response_model=List[getIndice])
def list_indice(db: Session = Depends(get_db)):
    return (
        db.query(
            Indice.name,
            Indice.description,
            Indice.created_at,
            Indice.updated_at,
            Indice.alias,
            case((Indice.evalscript.isnot(None), True), else_=False).label("process"),
            case((Indice.statistical_evalscript.isnot(None), True), else_=False).label(
                "statistics"
            ),
            satellite.satellite,
        )
        .filter(satellite.name == Indice.satellite)
        .order_by(Indice.name)
        .all()
    )


@route.get("/statistics")
def get_indice(
    start_date: date,
    end_date: date,
    index: str,
    farm_id: str,
    api_key: str,
    interval: str = "P1D",
    db: Session = Depends(get_db),
):

    curr_indice = check_indice(db, index, "statistics")

    curr_satellite = (
        db.query(satellite).filter(satellite.name == curr_indice.satellite).first()
    )

    curr_farm_bbox = (
        db.query(Farm.bbox)
        .filter(Farm.id == farm_id)
        .join(User)
        .filter(User.apikey == api_key)
        .filter(User.id == Farm.user_id)
        .one()
    )

    if not curr_farm_bbox:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Farm not found"
        )

    config = SHConfig()
    config.sh_client_id = SENTINEL_HUB_CLIENT_ID
    config.sh_client_secret = SENTINEL_HUB_CLIENT_SECRET
    config.sh_base_url = curr_satellite.region_url

    collection = next(
        x for x in list(DataCollection) if x.api_id == curr_indice.satellite
    )

    calculations = {"default": {"histograms": {"default": {"nBins": 10}}}}

    request = SentinelHubStatistical(
        aggregation=SentinelHubStatistical.aggregation(
            evalscript=curr_indice.statistical_evalscript,
            time_interval=(start_date, end_date),
            aggregation_interval=interval,
        ),
        input_data=[SentinelHubStatistical.input_data(collection)],
        bbox=BBox(curr_farm_bbox[0], "EPSG:4326"),  # type: ignore
        config=config,
        calculations=calculations,
    )

    result = request.get_data()[0]

    # TODO: Refactor response
    return result["data"]
