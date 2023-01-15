from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    JSON,
    String,
    BigInteger,
    DATE,
    Float,
    Computed,
    DateTime,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from db import Base
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum


def generate_uuid():
    return str(uuid.uuid4().hex)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password = Column(String)
    name = Column(String, unique=True, index=True)
    site = Column(String)
    country = Column(String)
    apikey = Column(String, default=generate_uuid)


class Role(enum.Enum):
    farmer = "farmer"
    agronomist = "agronomist"
    superadmin = "superadmin"
    advisor = "advisor"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    ph = Column(BigInteger, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    apikey = Column(String, default=generate_uuid)
    role = Column(Enum(Role), default=Role.farmer, nullable=False)
    country_code = Column(Integer, nullable=False, default="91")


class Farm(Base):
    __tablename__ = "farm"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    geometry = Column(Geometry("POLYGON"))
    country = Column(String, nullable=False)
    state = Column(String, nullable=False)
    bbox = Column(JSON, nullable=False)
    area = Column(
        Float,
        Computed(
            "((ST_Area(ST_setSRID(geometry, 4326)::geography)) * 0.0002471054)", True
        ),
    )


class Crop(Base):
    __tablename__ = "crop"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String)
    yield_value = Column(Float)
    yield_unit = Column(String)
    yield_per = Column(String)


class Disease(Base):
    __tablename__ = "disease"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    diesease_type = Column(String, nullable=False)
    symptoms = Column(String, nullable=False)
    afftected_plants = Column(JSON, nullable=False)
    images = Column(JSON, nullable=False)
    causes = Column(String, nullable=False)
    organic_control = Column(String, nullable=False)
    chemical_control = Column(String, nullable=False)
    preventive_measures = Column(String, nullable=False)
    scientific_name = Column(String)


class satellite(Base):
    __tablename__ = "satellite"

    name = Column(String, primary_key=True)
    region_url = Column(String, nullable=False)
    satellite = Column(String, nullable=False)
    catalogue = Column(Boolean, default=True)


class Indice(Base):
    __tablename__ = "indice"

    name = Column(String, primary_key=True, nullable=False)
    evalscript = Column(String, nullable=False)
    satellite = Column(
        String, ForeignKey("satellite.name"), primary_key=True, nullable=False
    )
    statistical_evalscript = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )
    description = Column(String())
    source = Column(String())
    alias = Column(String)


class Advisory(Base):
    __tablename__ = "advisory"

    id = Column(String, primary_key=True, default=generate_uuid)
    crop = Column(String, ForeignKey("crop.id"), nullable=False)
    min_temp = Column(Float)
    max_temp = Column(Float)
    min_uv = Column(Float)
    max_uv = Column(Float)
    min_wind = Column(Float)
    max_wind = Column(Float)
    min_rainfall = Column(Float)
    max_rainfall = Column(Float)
    min_soilmoisture = Column(Float)
    max_soilmoisture = Column(Float)
    flag = Column(String)
    advisory = Column(String)
    stage_growth = Column(String)


class FarmCrop(Base):
    __tablename__ = "farm_crop"

    id = Column(String, primary_key=True, default=generate_uuid)
    farm_id = Column(String, ForeignKey("farm.id"), nullable=False)
    crop_id = Column(String, ForeignKey("crop.id"), nullable=False)
    sowing_date = Column(DATE, nullable=False)
    harvesting_date = Column(DATE)
    season = Column(Integer, nullable=False)


class CropStage(Base):
    __tablename__ = "crop_stages"

    id = Column(Integer, primary_key=True, index=True)
    crop = Column(String, ForeignKey("crop.id"), nullable=False)
    stages = Column(String, nullable=True)
    days = Column(Float, nullable=False)
    image = Column(String, nullable=True)
    title = Column(String, nullable=False)
    tasks = Column(String, nullable=True)


class CalendarData(Base):
    __tablename__ = "calendar_data"

    id = Column(Integer, primary_key=True, index=True)
    farm = Column(String, ForeignKey("farm.id"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE, nullable=False)


class Scouting(Base):
    __tablename__ = "scoutings"

    id = Column(Integer, primary_key=True, index=True)
    farm = Column(String, ForeignKey("farm.id"), nullable=False)
    geometry = Column(Geometry("POINT"), nullable=False)
    note_type = Column(String, nullable=False)
    comments = Column(String, nullable=True)
    attachment = Column(String, nullable=True)


class States(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    geom = Column(Geometry("MULTIPOLYGON"), nullable=False)
    name = Column(String, nullable=True)
    admin = Column(String, nullable=True)


class predict_disease(Base):
    __tablename__ = "predict_disease"

    class_name = Column(String, primary_key=True)
    disease = Column(String, nullable=False)
    crop_id = Column(String, ForeignKey("crop.id"))


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    message = Column(String, nullable=False)
    request_type = Column(String, nullable=True)


class HowToContact(enum.Enum):
    whatsapp = "whatsapp"
    zoom = "zoom"
    phone = "phone"


class Topic(enum.Enum):
    general = "general"
    disease = "disease"
    plantation = "plantation"
    harvesting = "harvesting"
    pesticides = "pesticides"
    waste = "waste"


class TypeOfExpert(enum.Enum):
    local = "local"
    international = "international"


class ScheduleCall(Base):
    __tablename__ = "schedule_calls"

    id = Column(Integer, primary_key=True, index=True)
    how_to_contact = Column(
        Enum(HowToContact), default=HowToContact.whatsapp, nullable=False
    )
    date_time = Column(DateTime(timezone=True), nullable=False)
    topic = Column(Enum(Topic), default=Topic.general, nullable=False)
    message = Column(String, nullable=False)
    type_of_expert = Column(
        Enum(TypeOfExpert), default=TypeOfExpert.local, nullable=False
    )
