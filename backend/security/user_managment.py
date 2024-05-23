from typing import Optional
import redis.asyncio
from os import getenv
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, RedisStrategy

from db.models import User, get_user_db


redis = redis.asyncio.from_url("redis://localhost:6379", decode_responses=True)
bearer_transport = BearerTransport(tokenUrl="auth/redis/login")


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="redis",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)


# TODO change to more secure and get it from env

SECRET = getenv("USERMANAGER_SECRET")


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


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, IntegerIDMixin](
    get_user_manager,
    [auth_backend],
    )

