from fastapi import APIRouter, UploadFile, File, HTTPException, status
from db.session import SessionLocal
from sqlalchemy import insert
from db.models import Images, Product
import os
from starlette.responses import FileResponse
from uuid import uuid4


# TODO: add file checker, images crud route, validation(file size)

router = APIRouter()
db = SessionLocal()


@router.post("/upload-file", status_code=status.HTTP_200_OK)
async def create_upload_file(product_id: int, file: UploadFile = File(...)):

    if not db.get(Product, product_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product does not exist")
    elif "image" not in file.content_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The file format is invalid")

    new_name = str(uuid4()) + os.path.splitext(file.filename)[1]
    file_path = os.path.join("static/images", new_name)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    await file.close()
    full_path = f"{os.path.dirname(os.path.abspath(file_path))}\\{new_name}"
    db.execute(insert(Images).values(product_id=product_id, path=full_path))
    db.commit()

    return {"path": full_path}


@router.get("/get-image/{image_id}")
async def get_image_by_id(image_id: int):
    file = db.get(Images, image_id)
    return FileResponse(file.path)


@router.get("/product_img/{product_id}", status_code=status.HTTP_200_OK)
async def get_product_img(product_id: int):
    product = db.get(Product, product_id)
    if product:
        return {"list of img": product.list_of_img}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product does not exist")
