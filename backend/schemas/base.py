from pydantic import BaseModel


class BaseProduct(BaseModel):
    name: str
    description: str
    price: float
    amount: float
