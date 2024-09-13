from typing import List

from ..base import BaseProduct
from pydantic import BaseModel, Field, constr, field_validator
import base64


class PhotoModel(BaseModel):
    photo_base64: str
    extensions: constr(pattern=r"^(jpg|jpeg|png)$", min_length=3, strip_whitespace=True)

    @field_validator('photo_base64')
    def validate_base64(cls, value: str) -> str:
        try:
            base64.b64decode(value, validate=True)
        except Exception:
            raise ValueError('Invalid Base64 string')
        return value


class SchemasProductIn(BaseProduct):
    photos: List[PhotoModel] = Field(..., min_items=1)


class AddRating(BaseModel):
    user_id: int
    product_id: int
    rating: int = Field(..., ge=0, lt=6)


# photos = ["1":{"photo_url":"21324tyhgfbdw", "extensions":"png"},"2":{"photo_url":"w1ewd", "extensions":"png"}]
