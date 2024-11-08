from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    # add validator for quantity currency urls
    product_id: int
    quantity: int
    # currency: str
    success_url: str
    cancel_url: str
