import sqlite3
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from . import schemas


def row_to_dict(row) -> Dict[str, Any]:
    if not row:
        return {}
    
    return {key: str(value) if key == 'created_at' else value for key, value in dict(row).items()}


def get_item_by_title(db: sqlite3.Connection, title: str) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM items WHERE title = ?"
    result = db.execute(query, (title,))
    item = result.fetchone()
    return row_to_dict(item) if item else None


def create_item(db: sqlite3.Connection, item: schemas.ItemCreate) -> Dict[str, Any]:
    existing_item = get_item_by_title(db, title=item.title)
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Item with title '{item.title}' already exists"
        )
        
    item_data = item.dict()
    
    query = """INSERT INTO items (title, description, is_active) 
              VALUES (?, ?, ?)"""
    result = db.execute(
        query, 
        (item_data['title'], item_data.get('description'), item_data.get('is_active', True))
    )
    
    created_id = result.lastrowid
    return get_item(db, created_id)


def get_items(db: sqlite3.Connection, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
    query = "SELECT * FROM items LIMIT ? OFFSET ?"
    result = db.execute(query, (limit, skip))
    items = result.fetchall()
    return [row_to_dict(item) for item in items]


def get_item(db: sqlite3.Connection, item_id: int) -> Dict[str, Any]:
    query = "SELECT * FROM items WHERE id = ?"
    result = db.execute(query, (item_id,))
    item = result.fetchone()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    return row_to_dict(item)


def update_item(db: sqlite3.Connection, item_id: int, item: schemas.ItemUpdate) -> Dict[str, Any]:
    existing_item = get_item(db, item_id)
    update_data = item.dict(exclude_unset=True)
    if not update_data:
        return existing_item
    
    if 'title' in update_data:
        title_check = get_item_by_title(db, title=update_data['title'])
        if title_check and title_check['id'] != item_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Item with title '{update_data['title']}' already exists"
            )
    
    update_fields = []
    params = []
    
    for key, value in update_data.items():
        if key in ['title', 'description', 'is_active']:
            update_fields.append(f"{key} = ?")
            params.append(value)
    
    if not update_fields:
        return existing_item
    
    query = f"UPDATE items SET {', '.join(update_fields)} WHERE id = ?"
    params.append(item_id)
    db.execute(query, params)
    
    return get_item(db, item_id)


def delete_item(db: sqlite3.Connection, item_id: int) -> Dict[str, Any]:
    item = get_item(db, item_id)
    
    # is_active = false 로 바꾸도록 할 것.
    query = "DELETE FROM items WHERE id = ?"
    db.execute(query, (item_id,))
    
    return item
