from fastapi import FastAPI, status, HTTPException, Request
from core.config import settings
from db.session import engine, SessionLocal
from db.base_class import Base
from db.models import User, Product, ProductsRating
from passlib.context import CryptContext
from schemas.models import NewUser, SchemasProduct, AddRating
from sqlalchemy import select, update, delete, insert


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
db = SessionLocal()


@app.post("/new-user", status_code=status.HTTP_200_OK, tags=["users"])
async def create_user(new_user: NewUser):
    all_data = db.query(User).all()
    if new_user.username in all_data or new_user.user_email in all_data:
        return HTTPException(status_code=400, detail="User already exists")
    else:
        new_user = User(username=new_user.username, password=get_password_hash(new_user.password),
                        user_email=new_user.user_email)
        db.add(new_user)
        db.commit()
        return {"msg": "Success"}


@app.get("/{user_id}", status_code=status.HTTP_200_OK, tags=["users"])
async def user_by_id(user_id: int):
    user = db.get(User, user_id)
    return {"msg": user}


@app.get("/", status_code=status.HTTP_200_OK, tags=["users"])
async def users():
    return {"msg": {"Users": db.query(User).all()}}


@app.patch("/change-user-password", status_code=status.HTTP_200_OK, tags=["users"])
async def change_password(new_password: str, user_id: int):
    user = db.query(User).filter_by(id=user_id).first()
    user.password = get_password_hash(new_password)
    db.commit()
    return {"msg": "Success"}


@app.delete("/delete-user", status_code=status.HTTP_200_OK, tags=["users"])
async def delete_user(user_id: int):
    user = db.get(User, user_id)
    db.delete(user)
    db.commit()
    return {"msg": "Success"}



@app.post("/create-product", status_code=status.HTTP_200_OK, tags=["products"])
async def create_product(product: SchemasProduct):
    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    return {"msg": "Success"}


@app.post("/add-rating", status_code=status.HTTP_200_OK, tags=["products"])
async def add_rating(rating: AddRating):
    db.execute(insert(ProductsRating).values(**rating.model_dump()))
    db.commit()
    return {"msg": "Success"}


@app.get("/products/", status_code=status.HTTP_200_OK, tags=["products"])
async def all_products(_: Request) -> list[SchemasProduct]:
    data = db.execute(select(Product)).all()
    return [SchemasProduct(id=x[0].id, name=x[0].name,
                           descriptions=x[0].descriptions,
                           price=x[0].price, average_rating=x[0].average_rating) for x in data]


@app.get("/get-product-by-id", status_code=status.HTTP_200_OK, tags=["products"])
async def get_product_by_id(product_id: int):
    return db.execute(select(Product).where(Product.id == product_id)).scalar()


@app.delete("/delete-product", status_code=status.HTTP_200_OK, tags=["products"])
async def delete_product(product_id: int):
    product = db.execute(delete(Product).where(Product.id == product_id))
    db.commit()
    return {"msg": "Success"}
