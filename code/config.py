from pydantic import BaseSettings


class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_pwd: str
    db_usr: str
    secret_key: str
    algorithm: str
    timeout: int
    SENTINEL_HUB_CLIENT_ID: str
    SENTINEL_HUB_CLIENT_SECRET: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    BUCKET_NAME: str
    AWS_REGION: str
    # Notification
    SENDINBLUE_KEY: str
    TWILIO_SID: str
    TWILIO_AUTH_TOKEN: str

    class Config:
        env_file = ".env"


setting = Settings()
