from .base import BaseCrud
from db.models import Cart
from sqlalchemy import select, insert, delete, update
from ..services.product import ProductCrud
from ..services.users import UserCrud
from fastapi import HTTPException, status, Depends
from schemas.request.cart import CartIn, CartInPatch
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_session, clear_cache


class CartCrud(BaseCrud):

    def __init__(self, db: AsyncSession = Depends(get_session), product_crud: ProductCrud = Depends(ProductCrud),
                 user_crud: UserCrud = Depends(UserCrud)):
        self.product_crud = product_crud
        self.user_crud = user_crud
        super().__init__(db)

    async def obj_exist(self, user_id: int, product_id: int):
        stmt = (select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id))
        result = await self.session.execute(stmt)
        result_orm = result.scalar()
        if result_orm:
            return True
        return False

    async def obj_get(self, user_id: int, product_id: int):
        existing_object = await self.obj_exist(user_id, product_id)
        if existing_object:
            stmt = (select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id))
            result = await self.session.execute(stmt)
            result_orm = result.scalar()
            return result_orm

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not Found")

    async def _update_cart_amount(self, product_id: int, user_id: int, amount: int):
        stmt = (
            update(Cart)
            .where(Cart.product_id == product_id, Cart.user_id == user_id)
            .values(amount=Cart.amount + amount)
            .returning(Cart))
        result = await self.session.execute(stmt)
        await self.session.commit()
        result_orm = result.scalar()

        return result_orm

    async def increase_amount(self, data: CartIn):
        result_orm = await self._update_cart_amount(data.product_id, data.user_id, data.amount)
        return result_orm

    async def update_amount(self, data: CartInPatch):
        existing_cart = await self.obj_exist(user_id=data.user_id, product_id=data.product_id)
        if not existing_cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")

        if data.amount > 0 or data.amount < 0:
            result_orm = await self._update_cart_amount(data.product_id, data.user_id, data.amount)
            if result_orm.amount <= 0:
                return await self.delete_product_from_cart(user_id=data.user_id, product_id=data.product_id)

            return result_orm

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount cannot be zero.")

    async def create_cart_obj(self, data: CartIn):

        await self.user_crud.user_exist(data.user_id)
        await self.product_crud.product_exists(product_id=data.product_id)
        cart_obj = await self.obj_exist(user_id=data.user_id, product_id=data.product_id)

        await clear_cache(f"cart:{data.user_id}", "carts:*", data.user_id)

        if cart_obj:
            result = await self.increase_amount(data)
            return result

        stmt = (insert(Cart).values(data.model_dump()).returning(Cart))

        result = await self.session.execute(stmt)
        await self.session.commit()

        result_orm = result.scalar()
        return result_orm

    async def get_cart(self, user_id: int):
        await self.user_crud.user_exist(user_id)

        stmt = (select(Cart).where(Cart.user_id == user_id))
        result = await self.session.execute(stmt)
        result_orm = result.fetchall()
        result_serialized = [cart[0].__dict__ for cart in result_orm]
        [data.pop("_sa_instance_state") for data in result_serialized]
        return result_serialized

    async def delete_product_from_cart(self, user_id: int, product_id: int):
        await clear_cache(f"cart:{user_id}", "carts:*", user_id)
        stmt = (delete(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id).returning(Cart))
        result = await self.session.execute(stmt)
        await self.session.commit()
        return {"Successfully deleted object": result.scalar()}
