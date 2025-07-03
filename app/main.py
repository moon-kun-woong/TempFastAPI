from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, crud
from .database import engine, get_db


models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Item API",
    description="FastAPI로 구현된 CRUD API",
    version="1.0.0"
)

@app.post("/items/", response_model=schemas.Item, status_code=status.HTTP_201_CREATED, tags=["Items"], description="아이템하나를 생성하는 API")
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, item=item)

@app.get("/items/", response_model=List[schemas.Item],status_code=status.HTTP_200_OK, tags=["Items"], description="아이템들을 조회하는 API")
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.get("/items/{item_id}", response_model=schemas.Item, status_code=status.HTTP_200_OK, tags=["Items"], description="아이템하나를 조회하는 API")
def read_item(item_id: int, db: Session = Depends(get_db)):
    return crud.get_item(db, item_id=item_id)

@app.put("/items/{item_id}", response_model=schemas.Item, tags=["Items"], status_code=status.HTTP_200_OK, description="아이템하나를 수정하는 API")
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    return crud.update_item(db, item_id=item_id, item=item)

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Items"], description="아이템하나를 삭제하는 API")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    crud.delete_item(db, item_id=item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.patch("/items/{item_id}", response_model=schemas.Item, tags=["Items"], status_code=status.HTTP_200_OK, description="아이템하나를 부분적으로 수정하는 API")
def patch_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    return crud.update_item(db, item_id=item_id, item=item)
