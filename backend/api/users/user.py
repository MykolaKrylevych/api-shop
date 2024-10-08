from fastapi import APIRouter, status, HTTPException, Depends
from schemas.models import UserCreate
from db.session import async_session
from passlib.context import CryptContext
from ..services.users import UserCrud

# TODO: Add ApiRouter, rolls, basic crud user/seller

router = APIRouter()

db = async_session()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# TODO: user create func from fastapi_users
# @router.post("", status_code=status.HTTP_200_OK)
# async def create_user(new_user: UserCreate, crud: UserCrud = Depends(UserCrud)):
#     test = await crud.check_if_user_exist(new_user)
#     if not test:
#         temp = new_user.model_dump()
#         temp["hashed_password"] = get_password_hash(temp.pop("password"))
#         result = await crud.create(temp)
#         return {"msg": f"{result.id}"}
#     else:
#         raise HTTPException(status_code=409, detail="User already exist")
#
#
# @router.get("/{user_id}", status_code=status.HTTP_200_OK)
# async def get_user_by_id(user_id: int, crud: UserCrud = Depends(UserCrud)):
#     result = await crud.get_one(user_id)
#     return result
#
#
# @router.get("", status_code=status.HTTP_200_OK)
# async def get_all(offset: int = 10, limit: int = 10, crud: UserCrud = Depends(UserCrud)):
#     result = await crud.get_all(offset=offset, limit=limit)
#     return result
