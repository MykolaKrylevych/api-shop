from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from db.session import engine, SessionLocal
from db.base_class import Base

from api.users import user
from api.products import product
from api.files import images


def create_tables():
    Base.metadata.create_all(bind=engine)


def start_application():
    start_app: FastAPI = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    create_tables()
    return start_app


app = start_application()
app.mount("/static", StaticFiles(directory="static"), name="static")
db = SessionLocal()

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

# TODO: add validation, fix bug with file_path

# @app.post("/files/")
# async def create_file(
#         file: Annotated[bytes, File()],
#         fileb: Annotated[UploadFile, File()],
#         token: Annotated[str, Form()],
# ):
#     return {
#         "file_size": len(file),
#         "token": token,
#         "fileb_content_type": fileb.content_type,
#     }
