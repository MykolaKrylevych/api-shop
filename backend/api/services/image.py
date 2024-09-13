from sqlalchemy import insert, select, update, delete
from db.models import Images
from base import BaseCrud


class ImageCrud(BaseCrud):
    async def add_image(self, photo_url, product_id):
        stmt = (insert(Images).values(photo_url=photo_url, product_id=product_id)).returning(Images)

        result = await self.session.execute(stmt)
        await self.session.commit()
        result_orm = result.scalar()
        return result_orm
