from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
import concurrent.futures
import requests
import time

from utils.api import get_user
from db import get_db


route = APIRouter(prefix="/weather", tags=["Weather"])


# Retrieve a single page and report the URL and contents
# move API key to env
def load_url(url, timeout):
    payload = {}

    headers = {
        "Authorization": "f4eaad50-8102-11ed-bce5-0242ac130002-f4eaadc8-8102-11ed-bce5-0242ac130002"
    }

    if url.__contains__("openweathermap"):
        response = requests.request("GET", url)

        return {"temp": response.json()}
    else:
        response = requests.request("GET", url, headers=headers)

        if response.status_code == 402:
            return {"soil": "API is not working"}
        else:
            return {"soil": response.json()}


@route.get("/")
def index(
    api_key: str,
    lat: float,
    lon: float,
    start: date,
    end: date,
    db: Session = Depends(get_db),
):
    get_user(db, api_key)

    final_data = []

    start_unix = time.mktime(start.timetuple())
    end_unix = time.mktime(end.timetuple())

    URLS = [
        f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely&appid=791614e3e399c384a60d51372ea06529&units=metric",
        f"https://api.stormglass.io/v2/bio/point?lat={lat}&lng={lon}&params=soilMoisture,soilTemperature,soilTemperature10cm&start={start_unix}&end={end_unix}&source=noaa",
    ]
    # return URLS
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}

        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]

            try:
                data = future.result()
                final_data.append(data)
            except Exception as exc:
                print("%r generated an exception: %s" % (url, exc))
            else:
                print("%r page is %d bytes" % (url, len(data)))

        return final_data
