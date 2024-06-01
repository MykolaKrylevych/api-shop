from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from db.session import engine, async_session, redis
from db.base_class import Base


from security.user_managment import fastapi_users, auth_backend
from api.users import user
from api.products import product
from api.files import images
# TODO: change it after test


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
app.mount("/static", StaticFiles(directory="static"), name="static")
db = async_session()


origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(product.router, prefix="/product", tags=["Products"])
app.include_router(images.router, prefix="/Image", tags=["Images"])
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/redis", tags=["auth"])


@app.on_event("startup")
async def startup():
    await create_tables()
    await redis.ping()


@app.on_event("shutdown")
async def shutdown():
    await redis.close()
