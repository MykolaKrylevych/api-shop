from .base import BaseCrud
from ..services.product import ProductCrud
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_session, clear_cache
from db.models import Category, ProductCategory
from fastapi import Depends, HTTPException, status
from sqlalchemy import select, delete, insert, update
from schemas.request.category import CategoryIn, CategoryProduct


class CategoryCrud(BaseCrud):
    def __init__(self, db: AsyncSession = Depends(get_session), product_crud: ProductCrud = Depends(ProductCrud)):
        self.product_crud = product_crud
        super().__init__(db)

    async def _obj_exist(self, name: str):
        stmt = (select(Category).where(Category.name == name))
        result = await self.session.execute(stmt)
        await self.session.commit()
        result_orm = result.scalar()
        if result_orm:
            return True
        return False

    async def _obj_exist_id(self, category_id: int):
        stmt = (select(Category).where(Category.id == category_id))
        result = await self.session.execute(stmt)
        await self.session.commit()
        result_orm = result.scalar()
        if result_orm:
            return True
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    async def _obj_product_category_exist(self, product_id: int, category_id: int):
        stmt = (select(ProductCategory).where(ProductCategory.product_id == product_id,
                                              ProductCategory.category_id == category_id))
        result = await self.session.execute(stmt)
        await self.session.commit()
        result_orm = result.scalar()
        if result_orm:
            return True
        return False

    async def create_category(self, data: CategoryIn):
        existing_category = await self._obj_exist(data.name)
        if existing_category:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This category already exist")
        stmt = (insert(Category).values(data.model_dump()).returning(Category))

        result = await self.session.execute(stmt)
        await self.session.commit()

        result_orm = result.scalar()
        return result_orm

    async def get_category(self, offset: int, limit: int):
        stmt = (select(Category).offset(offset).limit(limit))
        result = await self.session.execute(stmt)
        result_orm = result.scalars().all()
        return result_orm

    async def add_product(self, data: CategoryProduct):
        await self.product_crud.product_exists(data.product_id)
        await self._obj_exist_id(data.category_id)

        exiting_data = await self._obj_product_category_exist(product_id=data.product_id, category_id=data.category_id)
        if exiting_data:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This data already in database")

        stmt = (insert(ProductCategory).values(data.model_dump()).returning(ProductCategory))
        result = await self.session.execute(stmt)
        await self.session.commit()
        result_orm = result.scalar()
        return result_orm

    async def delete_category(self, category_id):
        await self._obj_exist_id(category_id=category_id)

        await clear_cache(f"category:{category_id}", "category:*", category_id)

        stmt = (delete(Category).where(Category.id == category_id).returning(Category))
        product_category_table_stmt = (delete(ProductCategory).where(ProductCategory.category_id == category_id))
        async with self.session as conn:
            await conn.execute(product_category_table_stmt)
            result = await conn.execute(stmt)
            await conn.commit()
        result_orm = result.scalar()
        return result_orm
