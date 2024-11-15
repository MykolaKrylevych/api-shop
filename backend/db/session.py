from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from core.config import settings
from aioredis import Redis, ConnectionPool, from_url
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi import Depends
from db.models import User
from typing import AsyncGenerator
import json

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
# print(f"Database URL is {str(SQLALCHEMY_DATABASE_URL)}")
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

async_session = async_sessionmaker(engine, class_=AsyncSession, autocommit=False, autoflush=False,
                                   expire_on_commit=False)

redis = from_url(settings.REDIS_URL, decode_responses=True)


# async def init_redis_pool() -> AsyncIterator[Redis]:
#     session = from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
#     yield session
#     session.close()
#     await session.wait_closed()

def create_redis():
    return ConnectionPool(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )


pool = create_redis()


def get_redis():
    return Redis(connection_pool=pool)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def clear_cache(pattern, pagination_pattern, cache_object_id,
                      redis_client: Redis = Depends(get_redis)):
    cache_key = pattern
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        await redis_client.delete(cache_key)

    pattern = pagination_pattern
    keys_to_delete = await redis_client.keys(pattern)

    for key in keys_to_delete:
        data = await redis_client.get(key)
        data = json.loads(data)
        for item in data:
            if cache_object_id == item["id"]:
                await redis_client.delete(key)
