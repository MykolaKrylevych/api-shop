from fastapi import APIRouter, status, HTTPException, Request
from sqlalchemy import select, delete, insert
from schemas.models import SchemasProduct, SchemasProductResponse, AddRating
from db.models import User, Product, ProductsRating, Images
from db.session import SessionLocal

# TODO: add category, base crud, validation, fix pydantic schemas, do normal response

router = APIRouter()
db = SessionLocal()


@router.post("/create-product", status_code=status.HTTP_200_OK)
async def create_product(product: SchemasProduct):
    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    return {"msg": "Success"}


@router.post("/add-rating", status_code=status.HTTP_200_OK)
async def add_rating(rating: AddRating):
    user = db.get(User, rating.user_id)
    product = db.get(Product, rating.product_id)
    if user is None or product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or product not found")
    db.execute(insert(ProductsRating).values(**rating.model_dump()))
    db.commit()
    return {"msg": "Success"}


@router.get("/products/", status_code=status.HTTP_200_OK)
async def all_products(_: Request) -> list[SchemasProductResponse]:
    data = db.execute(select(Product)).all()
    return [SchemasProductResponse(id=x[0].id, name=x[0].name,
                                   description=x[0].descriptions,
                                   price=x[0].price, average_rating=x[0].average_rating,
                                   path=x[0].list_of_img) for x in data]


@router.get("/get-product-by-id/{product_id}", status_code=status.HTTP_200_OK)
async def get_product_by_id(product_id: int):
    data = db.execute(select(Product).where(Product.id == product_id)).scalar()
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return SchemasProductResponse(id=data.id, name=data.name, description=data.descriptions, price=data.price,
                                  path=data.list_of_img,
                                  average_rating=data.average_rating)


# TODO: add cascade
@router.delete("/delete-product", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int):
    data = db.get(Product, product_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if data.ratings:
        db.execute(delete(ProductsRating).where(ProductsRating.product_id == data.id))
        db.commit()

    # TODO: add deleting files
    if data.images:
        db.execute(delete(Images).where(Images.product_id == data.id))
        db.commit()

    db.execute(delete(Product).where(Product.id == product_id))
    db.commit()
    return {"msg": "Success"}

