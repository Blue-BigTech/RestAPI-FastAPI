from pydantic import BaseModel, EmailStr, constr
from datetime import datetime, date
from typing import Optional, List, Literal

from models import Role


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    api_key: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    company_id: Optional[int] = None


class CompanySchema(BaseModel):
    email: str
    password: str
    name: str
    site: str
    country: str

    class Config:
        orm_mode = True


class GetCompany(CompanySchema):
    id: int
    apikey: str


class GetUser(BaseModel):
    email: Optional[EmailStr] = None
    ph: constr(min_length=10, max_length=13, regex="^[0-9]{10,13}$")  # type: ignore
    country_code: Optional[constr(min_length=1, max_length=4, regex="^\d{1,4}$")] = None  # type: ignore
    company_id: int

    class Config:
        orm_mode = True
        use_enum_values = True


class UserSchema(GetUser):
    password: str

    class Config:
        orm_mode = True


class uuidofuser(GetUser):
    apikey: str
    role: Optional[Role] = None
    is_active: bool = True


class loginUser(BaseModel):
    password: str
    ph: int


class PostFarm(BaseModel):
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    geometry: Optional[str]

    class Config:
        orm_mode = True


class getIndexValue(BaseModel):
    farm_id: str
    satellite_date: date
    index: Literal["true", "ndvi", "evi", "ndvigray"]


class Crop(BaseModel):
    name: str
    description: Optional[str]
    yield_value: Optional[float] = None
    yield_unit: Optional[
        Literal[
            "ton",
            "kg",
            "qt",
            "carton",
            "lbs",
            "q",
            "pounds",
            "gm",
            "nuts",
            "fruit",
            "qt herbage",
            "ton leaf",
            "ton dried leaves",
        ]
    ] = None
    yield_per: Optional[Literal["acre", "tree", "vine"]] = None


class PostCrop(Crop):
    class Config:
        orm_mode = True


class GetCrop(Crop):
    id: str

    class Config:
        orm_mode = True


class DiseaseSchema(BaseModel):
    name: str
    description: Optional[str]
    diesease_type: str
    symptoms: str
    afftected_plants: List[str]
    images: List[str]
    causes: str
    organic_control: str
    chemical_control: str
    preventive_measures: str
    scientific_name: str

    class Config:
        orm_mode = True


class GetDisease(DiseaseSchema):
    id: int


class PostAdvisorySchema(BaseModel):
    crop: str
    min_temp: Optional[float] = None
    max_temp: Optional[float] = None
    min_uv: Optional[float] = None
    max_uv: Optional[float] = None
    min_wind: Optional[float] = None
    max_wind: Optional[float] = None
    min_rainfall: Optional[float] = None
    max_rainfall: Optional[float] = None
    min_soilmoisture: Optional[float] = None
    max_soilmoisture: Optional[float] = None
    flag: Optional[str] = None
    stage_growth: Optional[str] = None
    advisory: Optional[str] = None

    class Config:
        orm_mode = True


class PostFarmCrop(BaseModel):
    crop: str
    sowing_date: date
    harvesting_date: Optional[date] = None
    season: int

    class Config:
        orm_mode = True


class StoreFarmCrop(PostFarmCrop):
    farm_id: str
    crop_id: str


class CropStageSchema(BaseModel):
    crop: str
    stages: Optional[str]
    days: float
    image: Optional[str]
    title: str
    tasks: Optional[str]

    class Config:
        orm_mode = True


class CalendarData(BaseModel):
    farm: str
    title: Literal[
        "Tilage",
        "Planting",
        "Fertilization",
        "Spraying",
        "Harvesting",
        "Planned Cost",
        "Other",
    ]
    description: Optional[str]
    start_date: date
    end_date: date


class GetCalendarData(CalendarData):
    id: int

    class Config:
        orm_mode = True


class PostCalendarData(CalendarData):
    class Config:
        orm_mode = True


class getIndice(BaseModel):
    name: str
    alias: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    process: bool
    statistics: bool
    satellite: str


class Scouting(BaseModel):
    farm: str
    geometry: str
    note_type: Literal[
        "Disease", "Pests", "Water logging", "Weeds", "Lodging", "Others"
    ]
    comments: Optional[str]
    attachment: Optional[str]


class PostScouting(Scouting):
    class Config:
        orm_mode = True


class GetScouting(Scouting):
    id: str

    class Config:
        orm_mode = True


class Notification(BaseModel):
    title: str
    description: str
    date_time: datetime
    polygon: str


class PostContact(BaseModel):
    name: str
    email: str
    phone: constr(min_length=10, max_length=13, regex="^[0-9]{10,13}$")  # type: ignore
    message: str
    request_type: Optional[str] = None

    class Config:
        orm_mode = True


class GetContact(PostContact):
    id: int


class PostScheduleCall(BaseModel):
    how_to_contact: Literal["whatsapp", "zoom", "phone"]
    date_time: datetime
    topic: Literal[
        "general", "disease", "plantation", "harvesting", "pesticides", "waste"
    ]
    message: str
    type_of_expert: Literal["local", "international"]


class GetScheduleCall(PostScheduleCall):
    id: int

    class Config:
        orm_mode = True
