from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from . import models, schemas


def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_items(db: Session, skip: int = 0, limit: int = 10):
    stmt = select(models.Item).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def get_item(db: Session, item_id: int):
    stmt = select(models.Item).where(models.Item.id == item_id)
    return db.execute(stmt).scalar_one_or_none()

def update_item(db: Session, item_id: int, item: schemas.ItemUpdate):
    update_data = item.model_dump(exclude_unset=True)
    if not update_data:
        return get_item(db, item_id)
    
    stmt = (
        update(models.Item)
        .where(models.Item.id == item_id)
        .values(**update_data)
        .returning(models.Item)
    )
    result = db.execute(stmt)
    db.commit()
    
    return result.scalar_one_or_none()


def delete_item(db: Session, item_id: int):
    stmt = (
        delete(models.Item)
        .where(models.Item.id == item_id)
        .returning(models.Item)
    )
    result = db.execute(stmt)
    db.commit()
    
    return result.scalar_one_or_none()
