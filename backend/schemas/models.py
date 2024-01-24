from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class NewUser(BaseModel):
    username: str
    password: str
    user_email: EmailStr


class SchemasProduct(BaseModel):
    id: Optional[int] = None
    name: str
    descriptions: str
    price: float
    average_rating: Optional[float] = None


class AddRating(BaseModel):
    user_id: int
    product_id: int
    rating: int = Field(..., ge=1, lt=6)
