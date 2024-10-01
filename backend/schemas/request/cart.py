from pydantic import BaseModel, Field


class CartIn(BaseModel):
    user_id: int
    product_id: int
    amount: int = Field(1, ge=1)


class CartInPatch(BaseModel):
    user_id: int
    product_id: int
    amount: int
