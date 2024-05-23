from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from db.session import engine, SessionLocal
from db.base_class import Base
import aioredis

from security.user_managment import fastapi_users, auth_backend
from api.users import user
from api.products import product
from api.files import images
# TODO: change it after test


def create_tables():
    Base.metadata.create_all(bind=engine)


def start_application():
    start_app: FastAPI = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    create_tables()
    return start_app


app = start_application()
app.mount("/static", StaticFiles(directory="static"), name="static")
db = SessionLocal()
redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)


@app.on_event("startup")
async def startup():
    await redis.ping()


@app.on_event("shutdown")
async def shutdown():
    await redis.close()

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




