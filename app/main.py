from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import sqlite3
from typing import List, Dict, Any

from . import schemas, crud
from .database import get_db

app = FastAPI(
    title="Item API",
    description="FastAPI로 구현된 CRUD API",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Items",
            "description": "아이템 관리 API"
        }
    ]
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "detail": exception.errors(),
            "message": "입력 데이터 유효성 검증에 실패했습니다."
        }),
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exception: HTTPException):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "detail": exception.detail,
            "status_code": exception.status_code
        },
    )

@app.post(
    "/items/", 
    response_model=schemas.Item, 
    status_code=status.HTTP_201_CREATED, 
    tags=["Items"], 
    summary="새 아이템 생성",
    description="새로운 아이템을 생성합니다.",
    responses={
        409: {
            "model": schemas.ConflictError,
            "description": "중복 제목"
        },
        422: {
            "model": schemas.ValidationErrorResponse,
            "description": "유효성 검증 실패"
        }
    }
)
def create_item(item: schemas.ItemCreate, db: sqlite3.Connection = Depends(get_db)):
    try:
        return crud.create_item(db=db, item=item)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"잘못된 입력값: {str(e)}"
        )

@app.get(
    "/items/", 
    response_model=List[schemas.Item],
    status_code=status.HTTP_200_OK, 
    tags=["Items"], 
    summary="아이템 목록 조회",
    description="전체 아이템 목록을 조회합니다."
)
def read_items(skip: int = 0, limit: int = 100, db: sqlite3.Connection = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.get(
    "/items/{item_id}", 
    response_model=schemas.Item, 
    status_code=status.HTTP_200_OK, 
    tags=["Items"], 
    summary="특정 아이템 조회",
    description="ID로 아이템을 조회합니다.",
    responses={
        404: {
            "model": schemas.HTTPError,
            "description": "아이템 없음"
        }
    }
)
def read_item(item_id: int, db: sqlite3.Connection = Depends(get_db)):
    return crud.get_item(db, item_id=item_id)

@app.put(
    "/items/{item_id}", 
    response_model=schemas.Item, 
    tags=["Items"], 
    status_code=status.HTTP_200_OK, 
    summary="아이템 수정",
    description="아이템을 수정합니다.",
    responses={
        404: {"model": schemas.HTTPError},
        409: {"model": schemas.ConflictError}
    }
)
def update_item(item_id: int, item: schemas.ItemUpdate, db: sqlite3.Connection = Depends(get_db)):
    return crud.update_item(db, item_id=item_id, item=item)

@app.delete(
    "/items/{item_id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    tags=["Items"], 
    summary="아이템 삭제",
    description="아이템을 삭제합니다.",
    responses={
        404: {"model": schemas.HTTPError}
    }
)
def delete_item(item_id: int, db: sqlite3.Connection = Depends(get_db)):
    crud.delete_item(db, item_id=item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.patch(
    "/items/{item_id}", 
    response_model=schemas.Item, 
    tags=["Items"], 
    status_code=status.HTTP_200_OK, 
    summary="아이템 부분 수정",
    description="아이템을 부분 수정합니다.",
    responses={
        404: {"model": schemas.HTTPError},
        409: {"model": schemas.ConflictError}
    }
)
def patch_item(item_id: int, item: schemas.ItemUpdate, db: sqlite3.Connection = Depends(get_db)):
    return crud.update_item(db, item_id=item_id, item=item)
