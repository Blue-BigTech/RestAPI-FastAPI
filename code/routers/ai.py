from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from db import get_db
from models import predict_disease, Crop
import numpy as np
import keras
import h5py
from tensorflow.keras.utils import load_img, img_to_array
from tensorflow.keras.models import load_model
from efficientnet.tfkeras import EfficientNetB4
import os
from uuid import uuid4


route = APIRouter(prefix="/ai", tags=["AI"])

PREDICT_DISEASE_MODEL = load_model("models/99.6_Disease_Classification_EfficientNet.h5")


def predict_image(img, class_names):
    # Needed for the model to work correctly but can't store in the Database because there's no Crop of type object
    class_names.append("Objects")
    # TODO: Sorting is super important
    class_names.sort()
    # The ML stuff
    i = load_img(img, target_size=(256, 256))
    i = img_to_array(i) / 255.0
    i = i.reshape(256, 256, 3)
    i = np.expand_dims(i, axis=0)
    x = PREDICT_DISEASE_MODEL.predict(i)[0]
    max_indices = np.argpartition(x, -3)[-3:]
    max_values = x[max_indices]

    result = list(
        map(
            lambda x, y: (class_names[x], np.round(y * 100, 2)), max_indices, max_values
        )
    )
    result.sort(key=lambda x: x[1], reverse=True)

    print(result)
    # TODO: Not sure of this, could be a problem later
    if result[0][0] == "Objects":
        raise HTTPException(
            status_code=status.HTTP_200_OK, detail=[{"crop": "Not a crop"}]
        )
    return result


@route.post("/detect-disease")
def detect_disease(image: UploadFile, db: Session = Depends(get_db)):

    if image.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file. Send an image in .png or .jpeg format",
        )

    ext = image.filename.split(".")[-1]
    filepath = f"./static/{str(uuid4())}.{ext}"
    try:
        contents = image.file.read()

        with open(filepath, "wb") as f:
            f.write(contents)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There was an error uploading the file",
        )
    finally:
        image.file.close()
    try:
        all_diseases = (
            db.query(
                predict_disease.class_name,
                predict_disease.disease,
                Crop.name.label("crop_name"),
            )
            .join(Crop)
            .filter(predict_disease.crop_id == Crop.id)
            .all()
        )
        class_names = [x[0] for x in all_diseases]
        predictions = predict_image(filepath, class_names)

        all_diseases_dict = {x[0]: x for x in all_diseases}

        result = []
        for x in predictions:
            result.append(
                {
                    "crop": all_diseases_dict[x[0]][2],
                    "disease": all_diseases_dict[x[0]][1],
                    "confidence": x[1],
                }
            )

        return result
    # To make sure the files are always deleted
    finally:
        os.remove(filepath)
