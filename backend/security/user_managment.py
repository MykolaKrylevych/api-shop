from typing import Optional
from db.session import redis
from core.config import settings
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, RedisStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from db.models import User
from db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession


bearer_transport = BearerTransport(tokenUrl="auth/redis/login")


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="redis",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)


SECRET = settings.USERMANAGER_SECRET


class UserManager(IntegerIDMixin, BaseUserManager[User, IntegerIDMixin]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(User, session)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, IntegerIDMixin](
    get_user_manager,
    [auth_backend],
    )

