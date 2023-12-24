from fastapi import FastAPI, status, HTTPException, Request
from core.config import settings
from db.session import engine, SessionLocal
from db.base_class import Base
from db.models import User, Product, ProductsRating
from passlib.context import CryptContext
from schemas.models import NewUser, NewProduct, AddRating


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
    print(db.query(Product).all())
    return {"msg": {"Users": db.query(User).all()}}


@app.patch("/change-user-password", status_code=status.HTTP_200_OK, tags=["users"])
async def change_password(new_password: str, user_id: int):
    user = db.query(User).filter_by(id=user_id).first()
    user.password = new_password
    db.commit()
    return {"msg": "Success"}


@app.delete("/delete-user", status_code=status.HTTP_200_OK, tags=["users"])
async def delete_user(user_id: int):
    user = db.get(User, user_id)
    db.delete(user)
    db.commit()
    return {"msg": "Success"}


# TODO: make it's working
@app.post("/create-product", status_code=status.HTTP_200_OK, tags=["products"])
async def create_product(product: NewProduct):
    new_product = Product(name=product.name, descriptions=product.descriptions)
    db.add(new_product)
    db.commit()
    return {"msg": "Success"}


@app.post("/add-rating", status_code=status.HTTP_200_OK, tags=["products"])
async def change_rating(rating):
    print(rating)
    return {"msg": "Success"}


@app.get("/products", status_code=status.HTTP_200_OK, tags=["products"])
async def all_products(_: Request):
    data = db.query(Product).all()
    return {"msg": {"Products": data}}
