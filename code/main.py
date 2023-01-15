from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache

from db import SessionLocal
from routers import (
    auth,
    admin,
    farm,
    satellite,
    crop,
    disease,
    weather,
    advisory,
    file_upload,
    scouting,
    calendar_data,
    notification,
    contact,
    schedule_call,
    # ai,
)

origins = [
    "http://localhost",
    "http://localhost:3000/",
]

# models.Base.metadata.create_all(bind=engine)
app = FastAPI()


@lru_cache()
def get_settings():
    return Settings()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(auth.route)
app.include_router(admin.route)
app.include_router(farm.route)
app.include_router(satellite.route)
app.include_router(crop.route)
app.include_router(disease.route)
app.include_router(weather.route)
app.include_router(calendar_data.route)
app.include_router(advisory.route)
app.include_router(scouting.route)
app.include_router(file_upload.route)
app.include_router(notification.route)
app.include_router(contact.route)
app.include_router(schedule_call.route)
# app.include_router(ai.route)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"data": "at home"}
