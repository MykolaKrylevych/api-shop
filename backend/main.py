from fastapi import FastAPI, status, HTTPException, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from db.session import engine, SessionLocal
from db.base_class import Base
from db.models import User, Product, ProductsRating
from passlib.context import CryptContext
from schemas.models import NewUser, SchemasProduct, SchemasProductResponse, AddRating
from sqlalchemy import select, update, delete, insert
import os


def create_tables():
    Base.metadata.create_all(bind=engine)


def start_application():
    start_app: FastAPI = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    create_tables()
    return start_app


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


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


@app.post("/new-user", status_code=status.HTTP_200_OK, tags=["Users"])
async def create_user(new_user: NewUser):
    all_data = db.query(User).all()
    for user in all_data:
        if new_user.username == user.username or new_user.user_email == user.username:
            raise HTTPException(status_code=400, detail="User already exists")
        else:
            new_user = User(username=new_user.username, password=get_password_hash(new_user.password),
                            user_email=new_user.user_email)
            db.add(new_user)
            db.commit()
            return {"msg": "Success"}


@app.get("/{user_id}", status_code=status.HTTP_200_OK, tags=["Users"])
async def user_by_id(user_id: int):
    user = db.get(User, user_id)
    return {"msg": user}


@app.get("/", status_code=status.HTTP_200_OK, tags=["Users"])
async def users():
    return db.query(User).all()


@app.patch("/change-user-password", status_code=status.HTTP_200_OK, tags=["Users"])
async def change_password(new_password: str, user_id: int):
    user = db.query(User).filter_by(id=user_id).first()
    user.password = get_password_hash(new_password)
    db.commit()
    return {"msg": "Success"}


@app.delete("/delete-user", status_code=status.HTTP_200_OK, tags=["Users"])
async def delete_user(user_id: int):
    user = db.get(User, user_id)
    if user:
        for rating in user.ratings:
            db.execute(delete(ProductsRating).where(ProductsRating.id==rating.id))
            db.commit()
        db.delete(user)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"msg": "Success"}


# TODO: fix pydantic schemas
@app.post("/create-product", status_code=status.HTTP_200_OK, tags=["Products"])
async def create_product(product: SchemasProduct):
    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    return {"msg": "Success"}


@app.post("/add-rating", status_code=status.HTTP_200_OK, tags=["Products"])
async def add_rating(rating: AddRating):
    db.execute(insert(ProductsRating).values(**rating.model_dump()))
    db.commit()
    return {"msg": "Success"}


@app.get("/products/", status_code=status.HTTP_200_OK, tags=["Products"])
async def all_products(_: Request) -> list[SchemasProductResponse]:
    data = db.execute(select(Product)).all()
    return [SchemasProductResponse(id=x[0].id, name=x[0].name,
                                   descriptions=x[0].descriptions,
                                   price=x[0].price, average_rating=x[0].average_rating) for x in data]


@app.get("/get-product-by-id/{product_id}", status_code=status.HTTP_200_OK, tags=["Products"])
async def get_product_by_id(product_id: int):
    data = db.execute(select(Product).where(Product.id == product_id)).scalar()
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return SchemasProductResponse(id=data.id, name=data.name, descriptions=data.descriptions, price=data.price,
                                  average_rating=data.average_rating)


@app.delete("/delete-product", status_code=status.HTTP_200_OK, tags=["Products"])
async def delete_product(product_id: int):
    data = db.get(Product, product_id)
    if data.ratings:
        for product_rating in data.ratings:
            db.execute(delete(ProductsRating).where(ProductsRating.id == product_rating.id))
            db.commit()
    db.execute(delete(Product).where(Product.id == product_id))
    db.commit()
    return {"msg": "Success"}


# TODO: add validation, fix bug with file_path
@app.post("/upload-file", tags=["Images"])
async def create_upload_file(file: UploadFile):
    file_path = os.path.join("static", file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    await file.close()
    full_path = f"{os.path.dirname(os.path.abspath(file_path))}\\{file.filename}"
    return {"path": full_path}

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
