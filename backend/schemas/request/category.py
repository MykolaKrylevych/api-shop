from pydantic import BaseModel


class CategoryIn(BaseModel):
    name: str


class CategoryProduct(BaseModel):
    category_id: int
    product_id: int
