from fastapi import APIRouter, status, HTTPException, Depends
from schemas.models import UserCreate
from db.models import User, ProductsRating
from db.session import async_session
from passlib.context import CryptContext
from sqlalchemy import delete, select, insert, update
from ..services.users import UserCrud

# TODO: Add ApiRouter, rolls, basic crud user/seller

router = APIRouter()

db = async_session()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# @router.post("/new-user", status_code=status.HTTP_200_OK)
# async def create_user(new_user: UserCreate):
#     all_data = db.query(User).all()
#     for user in all_data:
#         if new_user.username == user.username or new_user.user_email == user.username:
#             raise HTTPException(status_code=400, detail="User already exists")
#         else:
#             new_user = User(username=new_user.username, password=get_password_hash(new_user.password),
#                             user_email=new_user.user_email)
#             db.add(new_user)
#             db.commit()
#             return {"msg": "Success"}

@router.post("", status_code=status.HTTP_200_OK)
async def create_user(new_user: UserCreate, crud: UserCrud = Depends(UserCrud)):
    test = await crud.check_if_user_exist(new_user)
    if not test:
        temp = new_user.model_dump()
        temp["hashed_password"] = get_password_hash(temp.pop("password"))
        result = await crud.create(temp)
        return {"msg": f"{result.id}"}
    else:
        raise HTTPException(status_code=409, detail="User already exist")


# @router.get("/{user_id}", status_code=status.HTTP_200_OK)
# async def user_by_id(user_id: int):
#     user = db.get(User, user_id)
#     return {"msg": user}

@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: int, crud: UserCrud = Depends(UserCrud)):
    result = await crud.get_one(user_id)
    return result


# @router.get("/", status_code=status.HTTP_200_OK)
# async def users():
#     return db.query(User).all()
@router.get("", status_code=status.HTTP_200_OK)
async def get_all(offset: int = 10, limit: int = 10, crud: UserCrud = Depends(UserCrud)):
    result = await crud.get_all(offset=offset, limit=limit)
    return result


# TODO let it do fastapi_users
# @router.patch("/change-user-password", status_code=status.HTTP_200_OK)
# async def change_password(new_password: str, user_id: int):
#     user = db.query(User).filter_by(id=user_id).first()
#     user.password = get_password_hash(new_password)
#     db.commit()
#     return {"msg": "Success"}


# @router.delete("/delete-user", status_code=status.HTTP_200_OK)
# async def delete_user(user_id: int):
#     user = db.get(User, user_id)
#     if user:
#         for rating in user.ratings:
#             db.execute(delete(ProductsRating).where(ProductsRating.id == rating.id))
#             db.commit()
#         db.delete(user)
#         db.commit()
#     else:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     return {"msg": "Success"}
@router.delete("/{user_id}")
async def delete_user(user_id: int, crud: UserCrud = Depends(UserCrud)):
    result = await crud.delete_user(user_id)
    return {"Bye": f"{result}"}

