from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from fastapi import HTTPException, status
from . import models, schemas


def get_item_by_title(db: Session, title: str):
    stmt = select(models.Item).where(models.Item.title == title)
    return db.execute(stmt).scalar_one_or_none()


def create_item(db: Session, item: schemas.ItemCreate):
    existing_item = get_item_by_title(db, title=item.title)
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Item with title '{item.title}' already exists"
        )
        
    try:
        db_item = models.Item(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        raise e

def get_items(db: Session, skip: int = 0, limit: int = 10):
    stmt = select(models.Item).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()

def get_item(db: Session, item_id: int):
    stmt = select(models.Item).where(models.Item.id == item_id)
    item = db.execute(stmt).scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return item

def update_item(db: Session, item_id: int, item: schemas.ItemUpdate):
    db_item = get_item(db, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
        
    update_data = item.model_dump(exclude_unset=True)
    if not update_data:
        return db_item
    
    if 'title' in update_data:
        existing_item = get_item_by_title(db, title=update_data['title'])
        if existing_item and existing_item.id != item_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Item with title '{update_data['title']}' already exists"
            )
    
    try:
        stmt = (
            update(models.Item)
            .where(models.Item.id == item_id)
            .values(**update_data)
        )
        db.execute(stmt)
        db.commit()
        
        updated_item = db.query(models.Item).filter(models.Item.id == item_id).first()
        return updated_item
    except Exception as e:
        db.rollback()
        raise e


def delete_item(db: Session, item_id: int):
    db_item = get_item(db, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    try:
        stmt = (
            delete(models.Item)
            .where(models.Item.id == item_id)
        )
        db.execute(stmt)
        db.commit()        
        return db_item
    except Exception as e:
        db.rollback()
        raise e
