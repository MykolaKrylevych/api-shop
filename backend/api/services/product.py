from sqlalchemy import insert, select, update, delete
from api.services.base import BaseCrud
from schemas.models import SchemasProduct
from db.models import Product, ProductsRating
from schemas.models import AddRating


class ProductCrud(BaseCrud):
    async def create(self, new_product: SchemasProduct):
        stmt = (insert(Product).values(**new_product.model_dump()).returning(Product))

        result = await self.session.execute(stmt)
        await self.session.commit()

        result_orm = result.scalar()
        return result_orm

    async def get_all(self, offset: int, limit: int):
        # TODO: in future create a image relations with product
        # stmt = (
        #     select(Product)
        #     .options(selectinload(Product.images))
        #     .offset(offset)
        #     .limit(limit)
        # )
        stmt = (select(Product).offset(offset).limit(limit))
        result = await self.session.execute(stmt)
        result_orm = result.scalars().all()
        return result_orm

    async def get_one(self, product_id: int):
        stmt = (select(Product).where(Product.id == product_id))

        result = await self.session.execute(stmt)
        result_orm = result.scalar()

        return result_orm

    async def update(self, product_id: int, product_name: str, product_price: float, product_description: str):
        stmt = (update(Product).where(Product.id == product_id).values(
            name=product_name, price=product_price,
            description=product_description)).returning(Product)
        result = await self.session.execute(stmt)
        await self.session.commit()
        result_orm = result.scalar()
        return result_orm

    async def delete(self, product_id: int):
        stmt = (delete(Product).where(Product.id == product_id).returning(Product))

        result = await self.session.execute(stmt)
        await self.session.commit()

        result_orm = result.scalar()
        return result_orm

    async def create_rating(self, data: AddRating):
        stmt = (insert(ProductsRating).values(**data.model_dump()).returning(ProductsRating))
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar()
