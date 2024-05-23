from fastapi import APIRouter, status, HTTPException, Depends
from schemas.models import UserCreate
from db.models import User, ProductsRating
from db.session import SessionLocal
from passlib.context import CryptContext
from sqlalchemy import delete, select, insert, update

# TODO: Add ApiRouter, rolls, basic crud user/seller

router = APIRouter()

db = SessionLocal()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


@router.post("/new-user", status_code=status.HTTP_200_OK)
async def create_user(new_user: UserCreate):
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


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def user_by_id(user_id: int):
    user = db.get(User, user_id)
    return {"msg": user}


@router.get("/", status_code=status.HTTP_200_OK)
async def users():
    return db.query(User).all()


@router.patch("/change-user-password", status_code=status.HTTP_200_OK)
async def change_password(new_password: str, user_id: int):
    user = db.query(User).filter_by(id=user_id).first()
    user.password = get_password_hash(new_password)
    db.commit()
    return {"msg": "Success"}


@router.delete("/delete-user", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int):
    user = db.get(User, user_id)
    if user:
        for rating in user.ratings:
            db.execute(delete(ProductsRating).where(ProductsRating.id == rating.id))
            db.commit()
        db.delete(user)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"msg": "Success"}

