from sqlalchemy import insert, select, update, delete, or_
from api.services.base import BaseCrud
from db.models import User
from schemas.models import UserCreate


class UserCrud(BaseCrud):
    async def create(self, user):
        stmt = (insert(User).values(**user).returning(User))

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.scalar()

    async def get_all(self, offset: int, limit: int):
        stmt = (select(User).offset(offset).limit(limit))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_one(self, user_id):
        stmt = (select(User).where(User.id == user_id))

        result = await self.session.execute(stmt)

        return result.scalar()

    async def delete_user(self, user_id: int):
        stmt = (delete(User).where(User.id == user_id).returning(User))

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.scalar()

    async def check_if_user_exist(self, user: UserCreate):
        stmt = (select(User).filter(or_(User.username == user.username, User.email == user.email)))
        user = await self.session.execute(stmt)
        return user.scalar()
