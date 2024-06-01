from fastapi import APIRouter, status, HTTPException, Request, Depends
from sqlalchemy import select, delete, insert
from schemas.models import SchemasProduct, SchemasProductResponse, AddRating
from db.models import User, Product, ProductsRating, Images
from db.session import async_session
from ..services.product import ProductCrud

# TODO: add category, base crud, validation, fix pydantic schemas, do normal response

router = APIRouter()
db = async_session()


# @router.post("/create-product", status_code=status.HTTP_200_OK)
# async def create_product(product: SchemasProduct):
#     new_product = Product(**product.model_dump())
#
#     db.add(new_product)
#     await db.commit()
#     return {"msg": "Success"}
@router.post("", status_code=status.HTTP_200_OK)
async def create_product(data: SchemasProduct, crud: ProductCrud = Depends(ProductCrud)):
    result = await crud.create(data)
    await crud.session.commit()
    return {"msg": f"Success ID:{result.id}"}


# @router.post("/add-rating", status_code=status.HTTP_200_OK)
# async def add_rating(rating: AddRating):
#     user = db.get(User, rating.user_id)
#     product = db.get(Product, rating.product_id)
#     if user is None or product is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or product not found")
#     db.execute(insert(ProductsRating).values(**rating.model_dump()))
#     db.commit()
#     return {"msg": "Success"}
@router.post("/add-rating")
async def add_rating(data: AddRating, crud: ProductCrud = Depends(ProductCrud)):
    result = await crud.create_rating(data)
    return result


# @router.get("", status_code=status.HTTP_200_OK)
# async def all_products(_: Request) -> list[SchemasProductResponse]:
#     data = db.execute(select(Product)).all()
#     return [SchemasProductResponse(id=x[0].id, name=x[0].name,
#                                    description=x[0].description,
#                                    price=x[0].price, average_rating=x[0].average_rating,
#                                    path=x[0].list_of_img) for x in data]

# TODO fix args in case negative value
@router.get("", status_code=status.HTTP_200_OK)
async def all_products(offset: int = 10, limit: int = 10, crud: ProductCrud = Depends(ProductCrud)):
    data = await crud.get_all(offset=offset, limit=limit)
    return data


# @router.get("/get-product-by-id/{product_id}", status_code=status.HTTP_200_OK)
# async def get_product_by_id(product_id: int):
#     data = db.execute(select(Product).where(Product.id == product_id)).scalar()
#     if data is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
#     return SchemasProductResponse(id=data.id, name=data.name, description=data.description, price=data.price,
#                                   path=data.list_of_img,
#                                   average_rating=data.average_rating)


@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product_by_id(product_id: int, crud: ProductCrud = Depends(ProductCrud)):
    data = await crud.get_one(product_id)
    return data


# TODO: add cascade
# @router.delete("/delete-product", status_code=status.HTTP_200_OK)
# async def delete_product(product_id: int):
#     data = db.get(Product, product_id)
#     if not data:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
#
#     if data.ratings:
#         db.execute(delete(ProductsRating).where(ProductsRating.product_id == data.id))
#         db.commit()
#
#     # TODO: add deleting files
#     if data.images:
#         db.execute(delete(Images).where(Images.product_id == data.id))
#         db.commit()
#
#     db.execute(delete(Product).where(Product.id == product_id))
#     db.commit()
#     return {"msg": "Success"}

@router.delete("/{product_id}")
async def delete_product(product_id: int, crud: ProductCrud = Depends(ProductCrud)):
    result = await crud.delete(product_id)
    return result
