from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.config import settings, logger

from db.session import engine, async_session, redis
from db.base_class import Base
from db.models import User

from security.user_managment import auth_backend, fastapi_users

from api.products import product
from api.cart import cart
from api.category import category
from api.payment import payment

from schemas.models import UserCreate, UserRead, UserUpdate

from starlette.requests import Request

import time

# TODO: change it after test


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
app.mount("/static", StaticFiles(directory="static"), name="static")
db = async_session()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(product.router, prefix="/product", tags=["Products"])

app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(category.router, prefix="/category", tags=["Category"])
app.include_router(payment.router, prefix="/payment", tags=["Payment"])

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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"IP: {request.client.host} Request: {request.method} {request.url}")
    start_time = time.time()
    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(f"Completed in {process_time:.2f}s with status {response.status_code}")

    return response


@app.exception_handler(Exception)
async def log_exception(request: Request, exc: Exception):
    logger.error(f"Exception occurred: {exc} URL:{request.url}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


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
    logger.warning("Server is down")
