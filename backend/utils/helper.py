import base64
from fastapi import HTTPException
from typing import List
import os
import uuid
from constants import TEMP_FILE_FOLDER


def decode_photo(path, encoded_string):
    with open(path, "wb") as f:
        try:
            f.write(base64.b64decode(encoded_string.encode("utf-8")))
        except Exception as ex:
            raise HTTPException(400, "Invalid photo encoding")


def image_saver(list_of_img: List):
    list_of_path = []
    if list_of_img:
        for data in list_of_img:
            photo, extensions = data.photo_base64, data.extensions
            name = f"{uuid.uuid4()}.{extensions}"
            path = os.path.join(TEMP_FILE_FOLDER, name)
            decode_photo(path, photo)
            list_of_path.append(path)
    return list_of_path
