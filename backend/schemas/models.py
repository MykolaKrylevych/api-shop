from pydantic import BaseModel, EmailStr


class NewUser(BaseModel):
    username: str
    password: str
    user_email: EmailStr


class NewProduct(BaseModel):
    name: str
    descriptions: str


class AddRating(BaseModel):
    rating: int
    user_id: int
    product_id: int


