from fastapi import APIRouter, Depends, HTTPException, status
from ..services.cart import CartCrud
from security.user_managment import fastapi_users
from schemas.request.cart import CartIn, CartInPatch
from db.session import redis
import json

ADMIN = fastapi_users.current_user(superuser=True)
router = APIRouter()


@router.post("/")
async def add_product(data: CartIn, crud: CartCrud = Depends(CartCrud), superuser=Depends(ADMIN)):
    response = await crud.create_cart_obj(data)
    return response


@router.get("/{user_id}")
async def get_user_cart(user_id: int, crud=Depends(CartCrud), superuser=Depends(ADMIN)):
    cache_key = f"cart:user_id{user_id}"
    cached_data = await redis.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    response = await crud.get_cart(user_id)
    await redis.set(cache_key, json.dumps(response), ex=60 * 5)

    return response


@router.patch("/")
async def change_amount(data: CartInPatch, crud: CartCrud = Depends(CartCrud),
                        superuser=Depends(ADMIN)):
    existing_cart = await crud.obj_exist(user_id=data.user_id, product_id=data.product_id)
    if existing_cart:
        response = await crud.update_amount(data)
        return response
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")


@router.delete("/")
async def delete_product_cart(product_id: int, user_id: int, crud: CartCrud = Depends(CartCrud),
                              superuser=Depends(ADMIN)):
    await crud.user_crud.user_exist(user_id)
    existing_cart = await crud.obj_exist(product_id=product_id, user_id=user_id)
    if existing_cart:
        result_orm = await crud.delete_product_from_cart(product_id=product_id, user_id=user_id)
        return result_orm
