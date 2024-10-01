from pydantic import BaseModel, Field
from typing import Optional, List


from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    username: str
    balance: float
    iban: str
    # from fastapi_users
    # id: models.ID
    # email: EmailStr
    # is_active: bool = True
    # is_superuser: bool = False
    # is_verified: bool = False


class UserCreate(schemas.BaseUserCreate):
    username: str
    iban: str


class UserUpdate(schemas.BaseUserUpdate):
    pass
