from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from security.user_managment import fastapi_users
from ..services.category import CategoryCrud
from schemas.request.category import CategoryIn, CategoryProduct

from db.session import redis
import json

ADMIN = fastapi_users.current_user(superuser=True)

router = APIRouter()


@router.get("/")
async def get_category(offset: int = Query(0, ge=0), limit: int = Query(10, ge=1),
                       crud: CategoryCrud = Depends(CategoryCrud), superuser=Depends(ADMIN)):
    cached_key = f"category:offset:{offset}limit:{limit}"
    cached_data = await redis.get(cached_key)

    if cached_data:
        return json.loads(cached_data)

    response = await crud.get_category(offset, limit)
    data = jsonable_encoder(response)
    await redis.set(cached_key, json.dumps(data), ex=60 * 5)

    return response


@router.post("/")
async def create_category(data: CategoryIn, crud: CategoryCrud = Depends(CategoryCrud), superuser=Depends(ADMIN)):
    response = await crud.create_category(data)
    return response


@router.post("/product")
async def add_product_to_category(data: CategoryProduct, crud: CategoryCrud = Depends(CategoryCrud),
                                  superuser=Depends(ADMIN)):
    response = await crud.add_product(data)
    return response


@router.delete("/{category_id}")
async def delete_category(category_id: int, crud:CategoryCrud=Depends(CategoryCrud),superuser=Depends(ADMIN)):
    response = await crud.delete_category(category_id)
    return response