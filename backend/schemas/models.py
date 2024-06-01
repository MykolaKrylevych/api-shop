from pydantic import BaseModel, Field
from typing import Optional, List


from fastapi_users import schemas, IntegerIDMixin, models


class UserRead(schemas.BaseUser[models.ID]):
    username: str
    balance: float
    # from fastapi_users
    # id: models.ID
    # email: EmailStr
    # is_active: bool = True
    # is_superuser: bool = False
    # is_verified: bool = False


class UserCreate(schemas.BaseUserCreate):
    username: str


class UserUpdate(schemas.BaseUserUpdate):
    pass


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
    rating: int = Field(..., ge=0, lt=6)
