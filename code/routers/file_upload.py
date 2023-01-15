from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from botocore.exceptions import ClientError
import boto3
import os
import uuid

from config import setting
from utils.api import get_user
from db import get_db

route = APIRouter(prefix="/upload", tags=["Upload"])


@route.post("/")
def upload(api_key: str, file: UploadFile = File(...), db: Session = Depends(get_db)):

    get_user(db, api_key)

    try:
        contents = file.file.read()

        filepath = f"./static/uploads/{file.filename}"

        with open(filepath, "wb") as f:
            f.write(contents)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="There was an error uploading the file",
        )
    finally:
        file.file.close()

    filename, extension = os.path.splitext(file.filename)
    s3_filename = f"scouting-attachments/{str(uuid.uuid4()) + extension}"

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=setting.AWS_ACCESS_KEY,
        aws_secret_access_key=setting.AWS_SECRET_KEY,
    )

    try:
        s3_client.upload_file(filepath, setting.BUCKET_NAME, s3_filename)
        os.remove(filepath)
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="File Uploading was failed"
        )

    url = f"https://{setting.BUCKET_NAME}.s3.{setting.AWS_REGION}.amazonaws.com/{s3_filename}"

    return url
