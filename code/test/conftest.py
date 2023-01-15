from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from config import setting
from db import Base, get_db
from models import User, Company, Farm

SQLALCHEMY_DATABASE_URL = f"postgresql://{setting.db_usr}:{setting.db_pwd}@{setting.db_host}:{setting.db_port}/{setting.db_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():

        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture()
def company(session):
    company = {
        "email": "seed@test.com",
        "password": "seedcompanypassword",
        "name": "seedcompany",
        "site": "seedcompany.com",
        "country": "US",
    }

    db = session

    new_company = Company(**company)

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return new_company


@pytest.fixture
def superadmin(session, company):
    user = {
        "email": "suerpadmin@test.com",
        "ph": "911234567890",
        "password": "suerpadminpassword",
        "country_code": "91",
        "company_id": company.id,
        "role": "superadmin",
    }

    db = session

    admin = User(**user)

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin


@pytest.fixture
def farmer(session, company):
    user = {
        "email": "farmer@test.com",
        "ph": "911234567890",
        "password": "farmerpassword",
        "country_code": "91",
        "company_id": company.id,
    }

    db = session

    new_user = User(**user)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@pytest.fixture
def farm(session, farmer):
    farm = {
        "user_id": farmer.id,
        "company_id": farmer.company_id,
        "name": "farm",
        "description": "farm description",
        "geometry": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
        "bbox": "",
        "country": "US",
        "state": "VA",
    }

    db = session

    new_farm = Farm(**farm)

    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)

    return new_farm


# Admin
@pytest.fixture
def success_create_company() -> dict:
    payload = {
        "email": "company@test.com",
        "password": "companypassword",
        "name": "company",
        "site": "company.com",
        "country": "US",
    }

    return payload


# scouting
@pytest.fixture
def success_create_scouting(farm) -> dict:
    payload = {
        "farm": farm.id,
        "geometry": "POINT(0 0)",
        "note_type": "Disease",
        "comments": "comments",
        "attachment": "attachment",
    }

    return payload


@pytest.fixture
def invalid_geometry_create_scouting(farm) -> dict:
    payload = {
        "farm": farm.id,
        "geometry": "POINT(0, 0)",
        "note_type": "Disease",
        "comments": "comments",
        "attachment": "attachment",
    }

    return payload


@pytest.fixture
def invalid_note_type_create_scouting(farm) -> dict:
    payload = {
        "farm": farm.id,
        "geometry": "POINT(0 0)",
        "note_type": "invalid",
        "comments": "comments",
        "attachment": "attachment",
    }

    return payload


# notification
@pytest.fixture
def success_send_notification() -> dict:
    payload = {
        "title": "title",
        "description": "description",
        "date_time": "2022-03-01 00:00:00",
        "polygon": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
    }

    return payload


@pytest.fixture
def invalid_title_send_notification() -> dict:
    payload = {
        "title": "",
        "description": "description",
        "date_time": "2022-03-01 00:00:00",
        "polygon": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
    }

    return payload


@pytest.fixture
def invalid_description_send_notification() -> dict:
    payload = {
        "title": "title",
        "description": "",
        "date_time": "2022-03-01 00:00:00",
        "polygon": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
    }

    return payload


@pytest.fixture
def invalid_datetime_send_notification() -> dict:
    payload = {
        "title": "title",
        "description": "description",
        "date_time": "invalid",
        "polygon": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
    }

    return payload


@pytest.fixture
def invalid_polygon_send_notification() -> dict:
    payload = {
        "title": "Hello",
        "description": "Hello Description",
        "date_time": "2022-03-01 00:00:00",
        "polygon": "invalid",
    }

    return payload


# contact
@pytest.fixture
def success_create_contact() -> dict:
    payload = {
        "name": "name",
        "email": "email@test.com",
        "phone": "1234567890",
        "message": "test message",
    }

    return payload


@pytest.fixture
def invalid_name_create_contact() -> dict:
    payload = {
        "name": "",
        "email": "email@test.com",
        "phone": "1234567890",
        "message": "test message",
    }

    return payload


@pytest.fixture
def invalid_phone_create_contact() -> dict:
    payload = {
        "name": "name",
        "email": "email@test.com",
        "phone": "invalid",
        "message": "test message",
    }

    return payload


@pytest.fixture
def invalid_message_create_contact() -> dict:
    payload = {
        "name": "name",
        "email": "email@test.com",
        "phone": "1234567890",
        "message": "",
    }

    return payload
