from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class NewUser(BaseModel):
    username: str
    password: str
    user_email: EmailStr


# TODO: add file
class SchemasProduct(BaseModel):
    name: str
    description: str
    price: float


class SchemasProductResponse(SchemasProduct):
    id: Optional[int] = None
    average_rating: Optional[float] = None
    path: List[str]


class AddRating(BaseModel):
    user_id: int
    product_id: int
    rating: int = Field(..., ge=1, lt=6)
