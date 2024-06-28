from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from core.config import settings
import aioredis
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi import Depends
from db.models import User
from typing import AsyncGenerator

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
print("Database URL is ", SQLALCHEMY_DATABASE_URL)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

async_session = async_sessionmaker(engine, class_=AsyncSession, autocommit=False, autoflush=False,
                                   expire_on_commit=False)

redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)
