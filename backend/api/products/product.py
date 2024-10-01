from fastapi import APIRouter, status, HTTPException, Depends, Query
from schemas.request.product import SchemasProductIn, AddRating, PatchProduct
from db.session import async_session
from ..services.product import ProductCrud
from security.user_managment import fastapi_users
from fastapi.encoders import jsonable_encoder
import json
from db.session import redis


ADMIN = fastapi_users.current_user(superuser=True)
router = APIRouter()
db = async_session()


@router.post("", status_code=status.HTTP_200_OK)
async def create_product(data: SchemasProductIn, crud: ProductCrud = Depends(ProductCrud), superuser=Depends(ADMIN)):
    result = await crud.create(data)
    return {"msg": f"Success ID:{result.id}"}


@router.post("/add-rating")
async def add_rating(data: AddRating, crud: ProductCrud = Depends(ProductCrud), superuser=Depends(ADMIN)):
    await crud.product_exists(data.product_id)
    existing_rating = await crud.rating_exists(product_id=data.product_id, user_id=data.user_id)
    if existing_rating:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Rating for this product by this user already exists")

    result = await crud.create_rating(data)
    return result


@router.get("", status_code=status.HTTP_200_OK)
async def all_products(offset: int = Query(0, ge=0), limit: int = Query(10, ge=1),
                       crud: ProductCrud = Depends(ProductCrud),
                       superuser=Depends(ADMIN)):
    cache_key = f"products:offset:{offset}:limit:{limit}"

    cached_data = await redis.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    data = await crud.get_all(offset=offset, limit=limit)
    if data:
        data = jsonable_encoder(data)
        for product in data:
            product["photo_urls"] = await crud.all_images(product["id"])
            product["rating"] = await crud.get_rating(product["id"])

    await redis.set(cache_key, json.dumps(data), ex=60 * 5)

    return data


@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product_by_id(product_id: int, crud: ProductCrud = Depends(ProductCrud), superuser=Depends(ADMIN)):
    cache_key = f"product:{product_id}"
    cached_data = await redis.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    data = await crud.get_one(product_id)
    data = jsonable_encoder(data)
    if data:
        data["photo_urls"] = await crud.all_images(product_id)
        data["rating"] = await crud.get_rating(product_id)

    await redis.set(cache_key, json.dumps(data), ex=3600)

    return data


@router.patch("/")
async def change_status(data: PatchProduct, crud: ProductCrud = Depends(ProductCrud), superuser=Depends(ADMIN)):
    response = await crud.change_product_status(data)
    return response


@router.delete("/{product_id}")
async def delete_product(product_id: int, crud: ProductCrud = Depends(ProductCrud), superuser=Depends(ADMIN)):
    data_in_db = await crud.product_exists(product_id)
    # if product_id in range of database object
    if data_in_db:
        result = await crud.delete(product_id)
        return jsonable_encoder(result)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product with this id was not found")
