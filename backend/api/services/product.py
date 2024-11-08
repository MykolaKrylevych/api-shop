from sqlalchemy import insert, select, update, delete, join, func
from api.services.base import BaseCrud
from schemas.request.product import SchemasProductIn, PatchProduct
from db.models import Product, ProductsRating, Images, ProductCategory
from db.session import clear_cache
from schemas.request.product import AddRating

from utils.helper import image_saver, image_delete
from fastapi import HTTPException, status


class ProductCrud(BaseCrud):
    async def create(self, new_product: SchemasProductIn):
        list_of_path = image_saver(new_product.photos)
        data = new_product.model_dump()
        data.pop("photos")

        stmt = (insert(Product).values(data).returning(Product))

        result = await self.session.execute(stmt)
        await self.session.commit()
        result_orm = result.scalar()
        # divide a function on smaller functions
        if list_of_path:
            for path in list_of_path:
                stmt = (insert(Images).values(photo_url=path, product_id=result_orm.id)).returning(Images)
                await self.session.execute(stmt)
                await self.session.commit()

        return result_orm

    async def get_all(self, offset: int, limit: int):
        stmt = (select(Product).offset(offset).limit(limit))
        result = await self.session.execute(stmt)
        result_orm = result.scalars().all()

        return result_orm

    async def get_one(self, product_id: int):
        stmt = (select(Product).where(Product.id == product_id))
        result = await self.session.execute(stmt)
        result_orm = result.scalar()
        if result_orm:
            return result_orm
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product with this id was not found")

    async def all_images(self, product_id: int):
        stmt = (select(Images.photo_url).where(Images.product_id == product_id))
        result = await self.session.execute(stmt)
        result_orm = result.fetchall()
        list_of_links = [str(link[0]) for link in result_orm]
        return list_of_links

    async def update(self, product_id: int, product_name: str, product_price: float, product_description: str):
        stmt = (update(Product).where(Product.id == product_id).values(
            name=product_name, price=product_price,
            description=product_description)).returning(Product)
        result = await self.session.execute(stmt)
        await self.session.commit()
        result_orm = result.scalar()
        return result_orm

    async def delete(self, product_id: int):
        stmt_product = (delete(Product).where(Product.id == product_id).returning(Product))
        stmt_img = (delete(Images).where(Images.product_id == product_id).returning(Images))
        stmt_rating = (delete(ProductsRating).where(ProductsRating.product_id == product_id).returning(ProductsRating))
        stmt_category = (
            delete(ProductCategory).where(ProductCategory.product_id == product_id).returning(ProductCategory))

        list_of_img = await self.all_images(product_id)
        await image_delete(list_of_img)

        await clear_cache(f"product:{product_id}", "products:*", product_id)

        async with self.session as conn:
            try:
                stmt_img_result = await conn.execute(stmt_img)
                stmt_rating_result = await conn.execute(stmt_rating)
                stmt_category_result = await conn.execute(stmt_category)
                stmt_product_result = await conn.execute(stmt_product)
                await conn.commit()
            except Exception as error:
                await conn.rollback()
                raise error

        result = [stmt_product_result.scalar(), stmt_img_result.scalar(), stmt_rating_result.scalar(),
                  stmt_category_result.scalar()]

        return result

    async def create_rating(self, data: AddRating):
        stmt = (insert(ProductsRating).values(**data.model_dump()).returning(ProductsRating))
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar()

    async def get_rating(self, product_id):
        stmt = (select(ProductsRating.rating).where(ProductsRating.product_id == product_id))
        result = await self.session.execute(stmt)
        result_orm = result.fetchall()
        list_of_data = [link[0] for link in result_orm]
        if len(list_of_data) == 0:
            return 0
        return sum(list_of_data) / len(list_of_data)

    async def product_exists(self, product_id: int) -> bool:
        stmt = (select(Product).where(Product.id == product_id))
        result = await self.session.execute(stmt)
        result_orm = result.scalar()
        if result_orm:
            return True
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product with this id was not found")

    async def rating_exists(self, product_id: int, user_id):
        stmt = (
            select(ProductsRating).where(ProductsRating.product_id == product_id,
                                         ProductsRating.user_id == user_id))
        result = await self.session.execute(stmt)
        return result.scalar()

    async def change_product_status(self, data: PatchProduct):
        # TODO finalize
        stmt = (
            update(Product)
            .where(Product.id == data.product_id)
            .values(status=data.status.name)
            .returning(Product)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        result_orm = result.scalar()
        return result_orm
