from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

from db.session import engine, async_session, redis
from db.base_class import Base
from db.models import User

from fastapi_users import FastAPIUsers, IntegerIDMixin
from security.user_managment import auth_backend, fastapi_users

# from api.users import user
from api.products import product
from api.files import images

from schemas.models import UserCreate, UserRead, UserUpdate


# TODO: change it after test


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
app.mount("/static", StaticFiles(directory="static"), name="static")
db = async_session()

# fastapi_users = FastAPIUsers[User, IntegerIDMixin](
#     get_user_manager,
#     [auth_backend],
#     )

# origins = [
#     "http://localhost",
#     "http://localhost:3000",
#     "http://127.0.0.1:3000"
# ]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(product.router, prefix="/product", tags=["Products"])
app.include_router(images.router, prefix="/Image", tags=["Images"])


# WASTODO broken access control delete&get_by_id fucking finally fixed :)
# fucking collision in users endpoint
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


current_active_user = fastapi_users.current_user(active=True)


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def startup():
    await create_tables()
    await redis.ping()


@app.on_event("shutdown")
async def shutdown():
    await redis.close()
