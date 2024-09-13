from fastapi import APIRouter, status, HTTPException, Depends
from schemas.request.product import SchemasProductIn
from schemas.request.product import AddRating
from db.session import async_session
from ..services.product import ProductCrud
from security.user_managment import fastapi_users
from fastapi.encoders import jsonable_encoder
# TODO: add category, base crud,

ADMIN = fastapi_users.current_user(superuser=True)
router = APIRouter()
db = async_session()


@router.post("", status_code=status.HTTP_200_OK)
async def create_product(data: SchemasProductIn, crud: ProductCrud = Depends(ProductCrud), superuser=Depends(ADMIN)):
    result = await crud.create(data)
    return {"msg": f"Success ID:{result.id}"}


@router.post("/add-rating")
async def add_rating(data: AddRating, crud: ProductCrud = Depends(ProductCrud), superuser=Depends(ADMIN)):
    result = await crud.create_rating(data)
    return result


# TODO fix args in case negative value
@router.get("", status_code=status.HTTP_200_OK)
async def all_products(offset: int = 0, limit: int = 10, crud: ProductCrud = Depends(ProductCrud),
                       superuser=Depends(ADMIN)):
    data = await crud.get_all(offset=offset, limit=limit)
    if data:
        data = jsonable_encoder(data)
        for product in data:
            product["photo_urls"] = await crud.all_images(product["id"])
            product["rating"] = await crud.get_rating(product["id"])
    return data


@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product_by_id(product_id: int, crud: ProductCrud = Depends(ProductCrud), superuser=Depends(ADMIN)):
    data = await crud.get_one(product_id)
    data = jsonable_encoder(data)
    if data:
        data["photo_urls"] = await crud.all_images(product_id)
        data["rating"] = await crud.get_rating(product_id)
    return data


@router.delete("/{product_id}")
async def delete_product(product_id: int, crud: ProductCrud = Depends(ProductCrud), superuser=Depends(ADMIN)):
    data_in_db = await crud.product_exists(product_id)
    # if product_id in range of database object
    if data_in_db:
        result = await crud.delete(product_id)
        return jsonable_encoder(result)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product with this id was not found")

